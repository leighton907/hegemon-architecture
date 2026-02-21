#!/usr/bin/env bash
# deploy_workspace.sh
# Deploys agent files from the repo into each agent's OpenClaw workspace.
# The repo is the source of truth. Run this after any corpus update.
#
# Usage:
#   ./scripts/deploy_workspace.sh              # deploy all agents
#   ./scripts/deploy_workspace.sh roxy         # deploy single agent
#   ./scripts/deploy_workspace.sh --check      # dry run, show what would change
#
# Workspace root is read from OPENCLAW_WORKSPACE_ROOT env var.
# Default: ~/.openclaw/workspaces
#
# Each agent gets its own workspace directory:
#   ~/.openclaw/workspaces/roxy/
#   ~/.openclaw/workspaces/sorin/
#   ...

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKSPACE_ROOT="${OPENCLAW_WORKSPACE_ROOT:-$HOME/.openclaw/workspaces}"
AGENTS=(roxy sorin brom vera astra)
DRY_RUN=false
SINGLE_AGENT=""

# ── Arg parsing ──────────────────────────────────────────────────────────────
for arg in "$@"; do
  case $arg in
    --check) DRY_RUN=true ;;
    --*)     echo "Unknown flag: $arg"; exit 1 ;;
    *)       SINGLE_AGENT="$arg" ;;
  esac
done

if [[ -n "$SINGLE_AGENT" ]]; then
  AGENTS=("$SINGLE_AGENT")
fi

# ── Files to deploy per agent ────────────────────────────────────────────────
# OpenClaw bootstrap files (injected automatically by runtime)
OPENCLAW_FILES=(
  "AGENTS.md"
  "SOUL.md"
  "IDENTITY.md"
  "TOOLS.md"
  "BOOTSTRAP.md"
)
# MEMORY.md and HEARTBEAT.md are merged into AGENTS.md — not separate workspace files
# BOOTSTRAP.md is only deployed if it doesn't already exist in workspace (one-time)

# Shared files (same content for all agents)
SHARED_FILES=(
  "USER.md"
)

# ── Deploy function ───────────────────────────────────────────────────────────
deploy_agent() {
  local agent="$1"
  local src_dir="$REPO_ROOT/agents/$agent"
  local dst_dir="$WORKSPACE_ROOT/$agent"

  if [[ ! -d "$src_dir" ]]; then
    echo "  ❌ Source directory not found: $src_dir"
    return 1
  fi

  echo ""
  echo "Agent: $agent"
  echo "  src: $src_dir"
  echo "  dst: $dst_dir"

  if [[ "$DRY_RUN" == false ]]; then
    mkdir -p "$dst_dir"
  fi

  # Deploy OpenClaw bootstrap files
  for fname in "${OPENCLAW_FILES[@]}"; do
    src="$src_dir/$fname"
    dst="$dst_dir/$fname"

    if [[ ! -f "$src" ]]; then
      echo "  ⚠️  MISSING in repo: agents/$agent/$fname"
      continue
    fi

    # BOOTSTRAP.md: only deploy if not already present in workspace
    if [[ "$fname" == "BOOTSTRAP.md" && -f "$dst" ]]; then
      echo "  ⏭️  SKIP $fname (already exists in workspace — first-run complete)"
      continue
    fi

    if [[ "$DRY_RUN" == true ]]; then
      if [[ -f "$dst" ]]; then
        if diff -q "$src" "$dst" > /dev/null 2>&1; then
          echo "  ✅ UNCHANGED $fname"
        else
          echo "  🔄 WOULD UPDATE $fname"
        fi
      else
        echo "  ➕ WOULD CREATE $fname"
      fi
    else
      cp "$src" "$dst"
      echo "  ✅ deployed $fname"
    fi
  done

  # Deploy shared files
  for fname in "${SHARED_FILES[@]}"; do
    src="$REPO_ROOT/agents/shared/$fname"
    dst="$dst_dir/$fname"

    if [[ ! -f "$src" ]]; then
      echo "  ⚠️  MISSING shared file: agents/shared/$fname"
      continue
    fi

    if [[ "$DRY_RUN" == true ]]; then
      echo "  🔄 WOULD DEPLOY shared/$fname"
    else
      cp "$src" "$dst"
      echo "  ✅ deployed shared/$fname"
    fi
  done
}

# ── Main ─────────────────────────────────────────────────────────────────────
echo ""
echo "Hegemon Workspace Deploy"
echo "========================"
echo "Repo:      $REPO_ROOT"
echo "Workspace: $WORKSPACE_ROOT"
echo "Mode:      $( [[ "$DRY_RUN" == true ]] && echo 'DRY RUN' || echo 'DEPLOY' )"

for agent in "${AGENTS[@]}"; do
  deploy_agent "$agent"
done

echo ""
if [[ "$DRY_RUN" == true ]]; then
  echo "Dry run complete. Run without --check to deploy."
else
  echo "Deploy complete."
  echo ""
  echo "Next steps:"
  echo "  1. Start agents: python main.py --agent roxy"
  echo "     (or via Docker: docker-compose up)"
  echo "  2. Each agent runs BOOTSTRAP.md on first session, then deletes it."
  echo "  3. Subsequent deploys skip BOOTSTRAP.md if already deleted."
fi
echo ""
