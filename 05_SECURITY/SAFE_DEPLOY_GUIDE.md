# Safe Deployment Guide
**Document ID:** SEC-003
**Version:** 1.0
**Status:** Active
**Authority:** Architect Command Manifest v2.5 — Section 5 (Operational Interfaces)

---

## Purpose

This guide defines the required security configuration for deploying Hegemon on a VPS. Every step here is mandatory before any agent goes live. Skipping steps creates attack surface that injection protection, tool policy, and governance controls cannot compensate for.

---

## VPS Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| RAM | 4 GB | 8 GB |
| CPU | 2 vCPU | 4 vCPU |
| Storage | 40 GB SSD | 80 GB SSD |
| OS | Ubuntu 22.04 LTS | Ubuntu 24.04 LTS |
| Provider | Any reputable VPS | Hetzner CX21 / DigitalOcean 4GB |

---

## Phase 1: Initial Server Hardening

### 1.1 Create a non-root user immediately

```bash
adduser hegemon
usermod -aG sudo hegemon
# Log out and log back in as hegemon — never operate as root
```

### 1.2 SSH key authentication only

```bash
# On your LOCAL machine, generate key if you don't have one:
ssh-keygen -t ed25519 -C "hegemon-vps"

# Copy public key to server:
ssh-copy-id hegemon@YOUR_VPS_IP

# On the SERVER, disable password auth and root login:
sudo nano /etc/ssh/sshd_config
# Set:
#   PasswordAuthentication no
#   PermitRootLogin no
#   PubkeyAuthentication yes

sudo systemctl restart sshd
```

### 1.3 Firewall — only open what you need

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh          # port 22
sudo ufw allow 80/tcp       # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp      # HTTPS
sudo ufw enable
sudo ufw status
```

Do not open any other ports. Agent-to-agent communication happens on the internal Docker network — never exposed to the internet.

### 1.4 Automatic security updates

```bash
sudo apt install unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
# Enable automatic updates when prompted
```

### 1.5 Fail2ban — block brute force attempts

```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## Phase 2: Docker Setup

### 2.1 Install Docker

```bash
sudo apt update
sudo apt install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add hegemon user to docker group
sudo usermod -aG docker hegemon
# Log out and back in for group change to take effect
```

### 2.2 Container isolation principles

Each Council agent runs in its own Docker container. Containers must:

- Have no shared volumes except explicitly approved mounts (corpus read-only)
- Communicate only through the internal Docker network (`hegemon-net`)
- Never mount the host filesystem except for designated corpus and data directories
- Run as non-root users inside the container

```yaml
# docker-compose.yml structure (reference)
networks:
  hegemon-net:
    driver: bridge
    internal: false  # allows outbound internet; agents need API access

services:
  roxy:
    build: ./agents/roxy
    container_name: openclaw-roxy
    networks: [hegemon-net]
    env_file: .env
    volumes:
      - ./corpus:/app/corpus:ro  # corpus is READ-ONLY
    restart: unless-stopped
    user: "1001:1001"  # non-root user

  sorin:
    build: ./agents/sorin
    container_name: openclaw-sorin
    networks: [hegemon-net]
    env_file: .env
    volumes:
      - ./corpus:/app/corpus:ro
    restart: unless-stopped
    user: "1001:1001"

  brom:
    build: ./agents/brom
    container_name: openclaw-brom
    networks: [hegemon-net]
    env_file: .env
    volumes:
      - ./corpus:/app/corpus:ro
      - ./data:/app/data  # ledger database — read/write
    restart: unless-stopped
    user: "1001:1001"

  vera:
    build: ./agents/vera
    container_name: openclaw-vera
    networks: [hegemon-net]
    env_file: .env
    volumes:
      - ./corpus:/app/corpus:ro
      - ./data:/app/data  # token_ledger access
    restart: unless-stopped
    user: "1001:1001"

  n8n:
    image: n8nio/n8n
    container_name: hegemon-n8n
    networks: [hegemon-net]
    env_file: .env
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: hegemon-nginx
    networks: [hegemon-net]
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/conf.d:/etc/nginx/conf.d:ro
      - ./certbot/conf:/etc/letsencrypt:ro
    restart: unless-stopped

volumes:
  n8n_data:
```

---

## Phase 3: Reverse Proxy and SSL

### 3.1 Nginx subdomain routing

```nginx
# /nginx/conf.d/hegemon.conf

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name _;
    return 301 https://$host$request_uri;
}

# n8n — workflow interface
server {
    listen 443 ssl;
    server_name n8n.yourdomain.ai;

    ssl_certificate /etc/letsencrypt/live/yourdomain.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.ai/privkey.pem;

    location / {
        proxy_pass http://hegemon-n8n:5678;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}

# Agent webhook endpoints — internal routing
# Each agent gets its own subdomain or path
server {
    listen 443 ssl;
    server_name agents.yourdomain.ai;

    ssl_certificate /etc/letsencrypt/live/yourdomain.ai/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.ai/privkey.pem;

    location /roxy { proxy_pass http://openclaw-roxy:8000; }
    location /sorin { proxy_pass http://openclaw-sorin:8001; }
    location /brom  { proxy_pass http://openclaw-brom:8002; }
    location /vera  { proxy_pass http://openclaw-vera:8003; }
}
```

### 3.2 SSL certificates via Certbot

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.ai -d n8n.yourdomain.ai -d agents.yourdomain.ai
# Follow prompts — certbot auto-renews via systemd timer
```

---

## Phase 4: Secrets Management

### 4.1 The .env file — structure and rules

Create a single `.env` file at the project root. This file is **never committed to git**.

```bash
# .env — NEVER COMMIT THIS FILE

# OpenAI
OPENAI_API_KEY=sk-...

# Hegemon internal webhooks (filled after n8n workflows are live)
HEGEMON_AUDIT_WEBHOOK=https://n8n.yourdomain.ai/webhook/hegemon-audit-log
HEGEMON_TOKEN_WEBHOOK=https://n8n.yourdomain.ai/webhook/hegemon-token-log
HEGEMON_INTAKE_WEBHOOK=https://n8n.yourdomain.ai/webhook/hegemon-task-intake

# Telegram
TELEGRAM_BOT_TOKEN=...

# Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# GitHub
GITHUB_TOKEN=ghp_...
GITHUB_OWNER=leighton907
GITHUB_REPO=hegemon-architecture

# Resend
RESEND_API_KEY=re_...
HEGEMON_FROM_EMAIL=system@yourdomain.ai

# HubSpot
HUBSPOT_API_KEY=...

# Database
POSTGRES_URL=postgresql://hegemon:PASSWORD@localhost:5432/hegemon_ledger
POSTGRES_PASSWORD=...  # use a strong generated password

# n8n
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=...  # use a strong generated password
N8N_ENCRYPTION_KEY=...  # 32-char random string
```

### 4.2 .gitignore — mandatory entries

```gitignore
# Secrets — NEVER COMMIT
.env
.env.*
*.key
*.pem
*.p12
secrets/
credentials/

# Runtime data
data/
*.sqlite
*.db

# Python
__pycache__/
*.pyc
.venv/
venv/

# Node
node_modules/

# Logs
logs/
*.log
```

### 4.3 Secret rotation policy

| Secret | Rotation Frequency | Trigger for Immediate Rotation |
|--------|--------------------|-------------------------------|
| OPENAI_API_KEY | Every 90 days | Any suspected compromise |
| TELEGRAM_BOT_TOKEN | Every 180 days | Bot behavior anomaly |
| GITHUB_TOKEN | Every 90 days | Repo access anomaly |
| RESEND_API_KEY | Every 90 days | Unusual email volume |
| HUBSPOT_API_KEY | Every 180 days | Unauthorized CRM access |
| POSTGRES_PASSWORD | Every 90 days | Any security event |
| N8N passwords | Every 90 days | Any security event |

When rotating a secret: update `.env`, restart affected containers, log the rotation in the Ledger as a `SECRET_ROTATED` audit event.

---

## Phase 5: n8n Security Configuration

### 5.1 Enable basic auth on n8n

Set in `.env`:
```
N8N_BASIC_AUTH_ACTIVE=true
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=<strong-password>
```

### 5.2 Restrict n8n webhook access

n8n webhook endpoints are public by default. Add an `X-Hegemon-Token` header check to every workflow's webhook trigger node:

In each Webhook trigger → Authentication → "Header Auth" → Header Name: `X-Hegemon-Token` → Header Value: a shared secret stored in `.env` as `HEGEMON_WEBHOOK_SECRET`.

All internal callers (agents, sub-agents) must include this header. External callers (Telegram, Discord) are handled by Workflows 02 and 03 which validate the platform's own authentication before passing to internal webhooks.

### 5.3 Workflow access control

- Workflows that trigger agent actions: set to **active** only when agents are deployed
- Workflows 01–10: do not expose their webhook URLs publicly — only share with authorized callers
- Disable any test workflows before going to production

---

## Phase 6: Postgres Setup

```bash
sudo apt install postgresql postgresql-contrib
sudo -u postgres psql

-- In psql:
CREATE USER hegemon WITH PASSWORD 'STRONG_PASSWORD_HERE';
CREATE DATABASE hegemon_ledger OWNER hegemon;
GRANT ALL PRIVILEGES ON DATABASE hegemon_ledger TO hegemon;
\q

-- Create required tables (from ledger_init.py and Workflow 05/10 specs):
-- Run: python3 scripts/ledger_init.py
-- Or manually:
psql -U hegemon -d hegemon_ledger -c "
CREATE TABLE IF NOT EXISTS audit_events (
  id SERIAL PRIMARY KEY,
  event_id VARCHAR(255) UNIQUE,
  actor VARCHAR(50) NOT NULL,
  action TEXT NOT NULL,
  outcome VARCHAR(20) NOT NULL,
  details JSONB,
  task_id VARCHAR(255),
  timestamp TIMESTAMP NOT NULL,
  integrity_hash VARCHAR(64) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS token_ledger (
  agent_name VARCHAR(50),
  date DATE,
  total_tokens_input INTEGER DEFAULT 0,
  total_tokens_output INTEGER DEFAULT 0,
  total_cost DECIMAL(10,4) DEFAULT 0,
  last_updated TIMESTAMP,
  budget_status VARCHAR(20),
  PRIMARY KEY (agent_name, date)
);
CREATE TABLE IF NOT EXISTS economic_metrics (
  id SERIAL PRIMARY KEY,
  metric_key TEXT,
  metric_value REAL,
  period TEXT
);
CREATE TABLE IF NOT EXISTS decision_trails (
  id SERIAL PRIMARY KEY,
  council_vote TEXT,
  proposal TEXT,
  outcome TEXT,
  ledger_ref TEXT
);
"
```

---

## Phase 7: Deployment Checklist

Run through this checklist before activating any agent:

**Server hardening:**
- [ ] Non-root user created and SSH key configured
- [ ] Password SSH login disabled
- [ ] UFW firewall active — only 22, 80, 443 open
- [ ] Fail2ban running
- [ ] Automatic security updates enabled

**Secrets:**
- [ ] `.env` file created with all required values
- [ ] `.gitignore` includes `.env` and all secret file patterns
- [ ] Confirmed `.env` is NOT in git history (`git log --all -- .env`)
- [ ] All placeholder values in `.env` replaced with real values

**Containers:**
- [ ] Docker and Docker Compose installed
- [ ] `docker-compose.yml` created with correct network and volume config
- [ ] All containers run as non-root users
- [ ] Corpus mounted read-only in all agent containers

**SSL and routing:**
- [ ] Certbot SSL certificates issued for all subdomains
- [ ] Nginx config tested (`nginx -t`)
- [ ] HTTPS working, HTTP redirecting

**n8n:**
- [ ] Basic auth enabled
- [ ] Webhook secret header configured on all active workflows
- [ ] All placeholder URLs wired per master placeholder map

**Database:**
- [ ] Postgres running with hegemon user and database
- [ ] All four tables created (audit_events, token_ledger, economic_metrics, decision_trails)
- [ ] `ledger_init.py` run successfully

**Agents:**
- [ ] Each agent container starts and logs successfully
- [ ] `HEGEMON_AUDIT_WEBHOOK` is live and accepting events
- [ ] `HEGEMON_TOKEN_WEBHOOK` is live and accepting events
- [ ] Injection guard tested: send a test CRITICAL pattern via Telegram and confirm block + audit log

**Final:**
- [ ] Astra corpus audit run — no broken references
- [ ] One end-to-end task tested: Telegram → Intake → Router → Agent → Ledger
- [ ] Token budget monitor confirming agent spend

---

## Post-Deployment: Monitoring

| Signal | Source | Threshold for Action |
|--------|--------|---------------------|
| Failed SSH attempts | Fail2ban logs | >10 in 1 hour |
| Container restarts | Docker logs | Any unexpected restart |
| Injection blocks | audit_events (outcome=BLOCKED) | >3 in 1 hour from same source |
| Budget exceeded | Vera / Workflow 10 | Immediate HITL |
| Ledger write failures | audit_events (action=LEDGER_WRITE, outcome=FAILURE) | Any occurrence |
| Disk usage | VPS dashboard | >80% |

Set up weekly review of `audit_events` for anomalous patterns. Astra's Corpus Audit Sub-Agent should run a governance check monthly.
