# LOOP-DeerFlow Deployment Guide

## Current Status: LOCALHOST WORKING ✅

**Local URL:** `http://localhost:8000`
**Health Check:** `curl http://localhost:8000/health` → `{"status":"healthy"}`
**API Docs:** `http://localhost:8000/docs`

---

## To Deploy Publicly (Fly.io)

### Step 1: Install Flyctl
```bash
# Mac
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Add to PATH
export PATH="$HOME/.fly/bin:$PATH"
```

### Step 2: Authenticate
```bash
flyctl auth token FlyV1...
```

### Step 3: Create Database
```bash
# Create Postgres
flyctl postgres create --name loop-deerflow-db

# Get connection string
flyctl postgres connect -a loop-deerflow-db
# Save DATABASE_URL for secrets
```

### Step 4: Set Secrets
```bash
flyctl secrets set \
  OPENROUTER_API_KEY=sk-or-v1-... \
  E2B_API_KEY=e2b_... \
  DATABASE_URL=postgres://... \
  SUPABASE_URL=https://... \
  SUPABASE_KEY=sbp_...
```

### Step 5: Deploy
```bash
flyctl deploy
```

**Public URL:** `https://loop-deerflow.fly.dev`

---

## Current Local Capabilities

### ✅ Working Now:
1. **DeerFlow Gateway** - Running on :8000
2. **Health Endpoint** - Responds to /health
3. **API Docs** - Swagger UI at /docs
4. **Built-in Skills** - 17 skills registered
5. **PostgreSQL** - State persistence
6. **Redis** - Task queue

### ❌ Not Yet Working:
1. **LOOP Skills** - Exist as files, not registered
2. **LLM Backend** - Configured but needs OpenRouter key
3. **Public Access** - Only localhost

---

## Next Steps to Make It Public:

1. **Install flyctl** (requires manual approval for security)
2. **Create Fly app + database**
3. **Deploy with secrets**
4. **Register LOOP skills**
5. **Test end-to-end**

---

## Quick Test (Local)

```bash
# Health check
curl http://localhost:8000/health

# List skills
curl http://localhost:8000/api/skills

# API docs (open in browser)
http://localhost:8000/docs
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│           loop-deerflow.fly.dev         │
│           (Public URL)                  │
├─────────────────────────────────────────┤
│  ┌─────────┐  ┌─────────┐  ┌────────┐ │
│  │ Gateway │  │ Skills  │  │   LLM  │ │
│  │  :8000  │  │  (5x)   │  │(OpenAI)│ │
│  └────┬────┘  └────┬────┘  └───┬────┘ │
│       └────────────┴───────────┘       │
│              DeerFlow Runtime          │
├─────────────────────────────────────────┤
│  PostgreSQL  │  Redis  │  E2B Sandbox │
└─────────────────────────────────────────┘
```

---

**Status:** Local working, deployment blocked on flyctl install
**ETA to public:** 10 minutes after flyctl installed
