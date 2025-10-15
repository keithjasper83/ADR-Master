# Upgrade Guide: v0.1.0 → v0.2.0

## Overview

Version 0.2.0 represents a major architectural change from **offline-first, single-user** to **online, multi-user, multi-project** architecture.

## Breaking Changes

### 1. Authentication Required

**v0.1.0:** No authentication, open access  
**v0.2.0:** JWT tokens or API keys required for all endpoints

**Action Required:**
- Register a user account
- Login to get authentication token
- Include token in `Authorization: Bearer <token>` header
- Or use session cookie after web login

### 2. API Endpoint Changes

All ADR endpoints now require `project_id` in the path:

| v0.1.0 | v0.2.0 |
|--------|--------|
| `POST /api/adr/draft` | `POST /api/adr/{project_id}/draft` |
| `POST /api/adr/compile` | `POST /api/adr/{project_id}/compile` |
| `POST /api/adr/lint` | `POST /api/adr/{project_id}/lint` |
| `POST /api/adr/promote` | `POST /api/adr/{project_id}/promote` |
| `POST /api/adr/sync` | `POST /api/adr/{project_id}/sync` |

### 3. Project-based Storage

**v0.1.0:** Single global ADR directory at `/ADR` and `/ADR/Draft`  
**v0.2.0:** Per-project directories specified when creating project

**Example:**
```
data/
├── project1/
│   └── ADR/
│       ├── Draft/
│       └── 001-decision.md
└── project2/
    └── ADR/
        ├── Draft/
        └── 001-decision.md
```

### 4. Database Schema

Complete database restructure. **Data migration required.**

**New Tables:**
- `users` - User accounts
- `projects` - Project metadata
- `project_members` - User-project relationships
- `project_invitations` - Invitation tokens

**Updated Tables:**
- `compilation_jobs` - Now linked to project and user
- `adr_metadata` - Now linked to project and author
- `integrations` - Now optionally project-scoped
- `action_logs` - Now linked to project and user

## Migration Guide

### Step 1: Backup Existing Data

```bash
# Backup old database
cp adr_master.db adr_master.db.v0.1.0.backup

# Backup ADR files
tar -czf adr_backup_v0.1.0.tar.gz ADR/
```

### Step 2: Install v0.2.0

```bash
git pull origin main
pip install -e ".[dev]"
```

### Step 3: Initialize New Database

```bash
# The new schema will be created on first run
# Old database is incompatible
rm adr_master.db
python -m uvicorn app.main:app --reload
```

### Step 4: Register First User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "secure-password"
  }'
```

Save the returned `access_token` for subsequent requests.

### Step 5: Create Project

```bash
TOKEN="your-access-token-here"

curl -X POST http://localhost:8000/api/projects \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Project",
    "description": "Migrated from v0.1.0",
    "root_path": "/path/to/data/my-project",
    "visibility": "private"
  }'
```

Save the returned `project_id` and `project_secret`.

### Step 6: Migrate ADR Files

```bash
# Copy old ADR files to new project directory
cp -r ADR/* /path/to/data/my-project/ADR/
```

### Step 7: Update Client Applications

If you have applications using the ADR-Master API:

**Before:**
```python
import httpx

response = httpx.post("http://localhost:8000/api/adr/draft", json={
    "title": "My ADR",
    "problem": "...",
    "context": "..."
})
```

**After:**
```python
import httpx

# Login first
auth_response = httpx.post("http://localhost:8000/api/auth/login", json={
    "email": "user@example.com",
    "password": "password"
})
token = auth_response.json()["access_token"]

# Use token and project_id
response = httpx.post(
    "http://localhost:8000/api/adr/1/draft",  # Note: /1/ is project_id
    headers={"Authorization": f"Bearer {token}"},
    json={
        "title": "My ADR",
        "problem": "...",
        "context": "..."
    }
)
```

## New Features in v0.2.0

### Multi-User Collaboration

- Multiple users can work on the same project
- Each user has their own authentication
- Project owners can invite other users

### Project Management

- Create multiple projects
- Each project has isolated ADR storage
- Project-level access control

### Flexible Authentication

- Email/password login with JWT tokens
- API keys for programmatic access
- Session cookies for web interface

### Project Invitations

**Invite via Email:**
```bash
curl -X POST http://localhost:8000/api/projects/1/invite \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "colleague@example.com",
    "role": "member"
  }'
```

**Join via Project Secret:**
```bash
curl -X POST http://localhost:8000/api/projects/1/join \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project_secret": "abc123xyz..."
  }'
```

## Configuration Changes

### Environment Variables

**New Required:**
- `SECRET_KEY` - For JWT signing (use `openssl rand -hex 32`)
- `BASE_URL` - Full URL of your installation

**New Optional:**
- `JWT_EXPIRATION_HOURS` - Token lifetime (default: 24)
- `INVITATION_EXPIRATION_DAYS` - Invitation validity (default: 7)
- `SESSION_COOKIE_SECURE` - HTTPS requirement (default: true)

**Removed:**
- Old single ADR directory paths
- Offline-specific settings

### Example .env

```env
# v0.2.0 Configuration
BASE_URL=https://adr.example.com
SECRET_KEY=your-secret-key-here-use-openssl-rand-hex-32
DATABASE_URL=sqlite:///./adr_master.db

# Optional
JWT_EXPIRATION_HOURS=24
MCP_BASE_URL=https://mcp-server.example.com/api
LLM_ENDPOINT=https://llm-api.example.com/generate
```

## Rollback Instructions

If you need to rollback to v0.1.0:

```bash
# Stop application
# Restore backups
cp adr_master.db.v0.1.0.backup adr_master.db
tar -xzf adr_backup_v0.1.0.tar.gz

# Checkout v0.1.0
git checkout v0.1.0
pip install -e .

# Restart
python -m uvicorn app.main:app --reload
```

## Support

For migration assistance:
- Check documentation in `docs/`
- Review API docs at `/docs` endpoint
- Open GitHub issue for migration problems

## Summary

v0.2.0 is a complete architectural reimagining:
- ✅ Multi-user collaboration
- ✅ Project-based organization  
- ✅ Robust authentication
- ✅ Online-ready architecture
- ❌ No longer offline-first (use case changed)
- ❌ Breaking API changes (planned)

Plan your migration carefully and test in a development environment first.
