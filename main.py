"""
main.py — Hegemon System Entry Point
──────────────────────────────────────
Boots all Council agents and starts their webhook listeners.

Usage:
    python main.py              # starts all agents
    python main.py --agent roxy # starts single agent (dev/debug)
    python main.py --check      # validates agent dirs and exits

Environment variables required (from .env):
    OPENAI_API_KEY
    HEGEMON_AUDIT_WEBHOOK
    HEGEMON_TOKEN_WEBHOOK
    HEGEMON_WEBHOOK_SECRET   # X-Hegemon-Token header value
"""

import os
import sys
import argparse
import logging
import pathlib
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import json

from openclaw_core.engine import OpenClawEngine

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("logs/hegemon.log", mode="a"),
    ]
)
logger = logging.getLogger("hegemon.main")

REPO_ROOT = pathlib.Path(__file__).resolve().parent

# ── Agent registry ────────────────────────────────────────────────────────────
# name → port (each agent listens on its own port behind Nginx)
AGENT_REGISTRY = {
    "roxy":  8000,
    "sorin": 8001,
    "brom":  8002,
    "vera":  8003,
    "astra": 8004,
}

WEBHOOK_SECRET = os.getenv("HEGEMON_WEBHOOK_SECRET", "")


# ── Webhook handler ───────────────────────────────────────────────────────────

class AgentHandler(BaseHTTPRequestHandler):
    """
    Minimal HTTP handler that receives POST requests and routes them
    to the agent's engine.run() method.

    Nginx sits in front and routes:
        /roxy  → openclaw-roxy:8000
        /sorin → openclaw-sorin:8001
        /brom  → openclaw-brom:8002
        /vera  → openclaw-vera:8003
        /astra → openclaw-astra:8004
    """
    engine: OpenClawEngine = None   # set on class before instantiating server

    def do_POST(self):
        # Validate X-Hegemon-Token header
        token = self.headers.get("X-Hegemon-Token", "")
        if WEBHOOK_SECRET and token != WEBHOOK_SECRET:
            self._respond(401, {"error": "Unauthorized"})
            return

        # Parse body
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._respond(400, {"error": "Invalid JSON"})
            return

        task_id      = payload.get("task_id", "")
        input_source = payload.get("origin", "webhook")
        user_input   = payload.get("task_description", payload.get("message", ""))

        if not user_input:
            self._respond(400, {"error": "Missing task_description or message field"})
            return

        # Run through engine
        output = self.engine.run(
            user_input=user_input,
            input_source=input_source,
            task_id=task_id,
        )

        self._respond(200, {
            "agent": self.engine.agent_id,
            "task_id": task_id,
            "response": output,
        })

    def do_GET(self):
        """Health check endpoint."""
        if self.path == "/health":
            self._respond(200, {"status": "ok", "agent": self.engine.agent_id})
        else:
            self._respond(404, {"error": "Not found"})

    def _respond(self, code: int, body: dict):
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(data))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, format, *args):
        # Redirect access logs to Python logger
        logger.debug(f"[{self.engine.agent_id}] {format % args}")


# ── Boot helpers ──────────────────────────────────────────────────────────────

def boot_agent(name: str, port: int):
    """Initialize engine and start HTTP listener for one agent."""
    logger.info(f"Booting agent: {name} on port {port}")
    try:
        engine = OpenClawEngine(name)
    except FileNotFoundError as e:
        logger.error(f"Cannot boot {name}: {e}")
        sys.exit(1)

    # Attach engine to a handler subclass (one class per agent)
    handler = type(f"{name.capitalize()}Handler", (AgentHandler,), {"engine": engine})

    server = HTTPServer(("0.0.0.0", port), handler)
    logger.info(f"[{engine.agent_id}] Listening on port {port}")
    server.serve_forever()


def validate_agents():
    """Check all agent directories and required files exist. Exit 0 if OK."""
    required_files = ["SOUL.md", "IDENTITY.md", "HEARTBEAT.md", "MEMORY.md", "AGENT.md"]
    all_ok = True
    for name in AGENT_REGISTRY:
        agent_dir = REPO_ROOT / "agents" / name
        for fname in required_files:
            fpath = agent_dir / fname
            status = "✅" if fpath.exists() else "❌ MISSING"
            if not fpath.exists():
                all_ok = False
            print(f"  {status}  agents/{name}/{fname}")
    return all_ok


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Hegemon agent runtime")
    parser.add_argument("--agent",  help="Boot a single agent by name (dev mode)")
    parser.add_argument("--check",  action="store_true", help="Validate agent dirs and exit")
    parser.add_argument("--port",   type=int, help="Override port (single-agent mode only)")
    args = parser.parse_args()

    # Ensure log dir exists
    (REPO_ROOT / "logs").mkdir(exist_ok=True)
    (REPO_ROOT / "data").mkdir(exist_ok=True)

    if args.check:
        print("\nValidating agent directories...\n")
        ok = validate_agents()
        print(f"\n{'All files present.' if ok else 'Missing files — fix before deploying.'}")
        sys.exit(0 if ok else 1)

    if args.agent:
        # Single-agent mode (dev / Docker container per agent)
        name = args.agent.lower()
        if name not in AGENT_REGISTRY:
            logger.error(f"Unknown agent: {name}. Valid: {list(AGENT_REGISTRY.keys())}")
            sys.exit(1)
        port = args.port or AGENT_REGISTRY[name]
        boot_agent(name, port)   # blocks

    else:
        # All-agents mode — one thread per agent (local dev only)
        # In production each agent runs in its own Docker container
        # with: python main.py --agent roxy
        logger.info("Starting all agents in multi-thread mode (dev only)")
        threads = []
        for name, port in AGENT_REGISTRY.items():
            t = Thread(target=boot_agent, args=(name, port), daemon=True)
            t.start()
            threads.append(t)
        logger.info("All agents started. Press Ctrl+C to stop.")
        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            logger.info("Shutting down.")


if __name__ == "__main__":
    main()
