# Changelog

All notable changes to ADR-Master will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2024-10-15

### ⚠️ BREAKING CHANGES

Complete architectural redesign from offline-first single-user to online multi-user system.

**Migration required** - see `UPGRADE_v0.2.md` for detailed instructions.

### Added

#### Multi-User & Authentication
- **User Management**: Email/password registration and login
- **JWT Authentication**: Secure token-based authentication
- **API Keys**: Generate API keys for programmatic access
- **Session Cookies**: Web-based authentication support
- **Password Hashing**: Secure password storage with bcrypt

#### Multi-Project Architecture
- **Project Management**: Create and manage multiple projects
- **Project Ownership**: Each project has an owner and members
- **Project Secrets**: Auto-generated secure secrets for joining projects
- **Project Invitations**: Invite users via email with expiring tokens
- **Project Access Control**: Owner/member roles with access verification

#### Updated API Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user
- `POST /api/auth/api-key/generate` - Generate API key
- `DELETE /api/auth/api-key/revoke` - Revoke API key
- `GET /api/projects` - List user's projects
- `POST /api/projects` - Create new project
- `GET /api/projects/{id}` - Get project details
- `POST /api/projects/{id}/invite` - Invite user to project
- `POST /api/projects/{id}/join` - Join project with secret
- `DELETE /api/projects/{id}` - Delete project

#### Database Schema
- `users` table for user accounts
- `projects` table for project metadata
- `project_members` association table for memberships
- `project_invitations` table for pending invitations
- Updated all existing tables with project/user references

### Changed

#### API Endpoints (Breaking)
- All ADR endpoints now require authentication
- All ADR endpoints scoped to `/{project_id}/`
  - `POST /api/adr/{project_id}/draft` (was `/api/adr/draft`)
  - `POST /api/adr/{project_id}/compile` (was `/api/adr/compile`)
  - `POST /api/adr/{project_id}/lint` (was `/api/adr/lint`)
  - `POST /api/adr/{project_id}/promote` (was `/api/adr/promote`)
  - `POST /api/adr/{project_id}/sync` (was `/api/adr/sync`)

#### Storage Model
- Changed from global ADR directories to per-project directories
- Each project specifies its own `root_path`, `adr_path`, `draft_path`
- ADR numbering now project-scoped (each project starts at 001)

#### Configuration
- Added `SECRET_KEY` for JWT signing (required)
- Added `BASE_URL` for invitation links (required)
- Added `JWT_EXPIRATION_HOURS` setting
- Added `INVITATION_EXPIRATION_DAYS` setting
- Added session cookie configuration
- Removed single global ADR directory paths
- Updated version to 0.2.0

### Removed

#### Offline-First Features
- Removed assumption of offline operation
- Removed air-gap deployment focus
- Updated to assume online connectivity
- External services (MCP, LLM) now expected to be available online

#### Documentation
- Removed offline-specific deployment guides (will be updated)
- Removed air-gap operation instructions (will be updated)

### Dependencies

#### Added
- `pyjwt>=2.8.0` - JWT token generation/verification
- `passlib[bcrypt]>=1.7.4` - Password hashing
- `python-jose[cryptography]>=3.3.0` - Cryptographic operations

### Migration

See `UPGRADE_v0.2.md` for complete migration guide from v0.1.0.

**Summary:**
1. Backup existing data
2. Register first user
3. Create project
4. Copy ADR files to new project directory
5. Update client applications with authentication

### Technical Details

- New `app/auth/` module for authentication logic
- Updated `app/services/adr_service.py` for project context
- Updated `app/api/adr.py` with project scoping
- New `app/api/auth.py` for authentication endpoints
- Enhanced `app/api/projects.py` with full project management

---

## [0.1.0] - 2024-01-15

### Added

#### Core Features
- **ADR Management**: Complete CRUD operations for Architecture Decision Records
  - Create drafts with MADR template
  - Edit and refine ADRs
  - Validate with comprehensive linting
  - Promote from draft to final
  - Sync with remote repositories

#### LLM Integration
- **Async Compilation**: Background job queue for LLM-powered ADR improvement
- **Job Status Tracking**: Real-time status monitoring for compilation jobs
- **Flexible LLM Support**: Works with Ollama, OpenAI-compatible endpoints

#### MCP Integration (Client)
- **Projects & Features**: Read-only access to external MCP servers
- **Proposal Submission**: Send ADRs and patches to MCP systems
- **Connection Status**: Real-time MCP connection monitoring

#### Plugin System
- **Integration Registry**: Register external tools and plugins
- **Hook System**: Four lifecycle hooks for extending functionality
  - `on_draft_create`: After draft creation
  - `on_compile_post`: After LLM compilation
  - `on_promote_pre`: Before promotion
  - `on_sync_post`: After sync operation
- **Example Plugin**: Risk analyzer plugin demonstration

#### API
- **RESTful API**: Complete REST API with OpenAPI documentation
- **Health Checks**: Standard health check endpoints
- **Interactive Docs**: Swagger UI at `/docs`

#### User Interface
- **Web Editor**: HTMX + Alpine.js + Tailwind CSS interface
- **Project Explorer**: Browse drafts and final ADRs
- **MCP Panel**: View and link features to ADRs
- **Settings Page**: Configuration management
- **Proposals Page**: Submit proposals to MCP
- **Integrations Page**: Manage plugins and integrations

#### Storage & Persistence
- **SQLite Database**: Local database for jobs, metadata, and logs
- **File-based ADRs**: Markdown files in `/ADR` and `/ADR/Draft`
- **Action Logging**: Comprehensive audit trail

#### Development Tools
- **Docker Support**: Dockerfile and docker-compose ready
- **Devcontainer**: VS Code devcontainer configuration
- **Build Tools**: Makefile, Nox, and Invoke tasks
- **Testing**: Pytest with fixtures and test infrastructure
- **CI/CD**: GitHub Actions with lint, test, security checks
- **Type Checking**: MyPy configuration
- **Code Quality**: Ruff, Black, Bandit integration

#### Documentation
- **Comprehensive README**: Quick start and feature overview
- **API Reference**: Complete API documentation
- **Deployment Guide**: Multiple deployment options
- **Offline Guide**: Air-gapped deployment instructions
- **MCP Integration Guide**: External MCP server integration
- **Example ADRs**: Sample ADRs and MADR templates
- **Plugin Example**: Full plugin implementation example

#### MCP Tools Adapter
- **Tool Definitions**: Five MCP tool definitions
  - `adr.generate`: Generate new ADR
  - `adr.compile`: Compile with LLM
  - `adr.lint`: Validate ADR
  - `adr.promote`: Promote to final
  - `adr.sync`: Sync with remote
- **Thin Wrapper**: Lightweight adapter for external MCP servers

#### Security & Offline
- **Offline-First**: Works completely without internet
- **No External Dependencies**: Self-contained except configured endpoints
- **Environment-based Config**: All secrets in `.env`
- **CORS Control**: Configurable CORS policies
- **CSRF Protection**: Basic CSRF token support

### Technical Details

- **Python 3.12+**: Modern Python with type hints
- **FastAPI**: High-performance async framework
- **SQLAlchemy 2.0**: Modern ORM with async support
- **Pydantic v2**: Data validation and settings
- **Alembic**: Database migrations
- **GitPython**: Git operations
- **HTTPX**: Async HTTP client
- **Jinja2**: Template engine

### Known Limitations

- Single-user SQLite database (suitable for teams up to 20)
- No real-time collaboration yet
- CDN dependencies for frontend (can be replaced with local assets)
- No built-in authentication (use reverse proxy)

### Future Roadmap (V2)

- Tree-sitter integration for code-aware previews
- LibCST/ts-morph for code diffs
- Web Workers for heavy operations
- Real-time collaboration
- ADR templates library
- Export to PDF/HTML
- ADR dependency graph visualization
- Advanced search and filtering
- Automated ADR suggestions from code changes

[0.1.0]: https://github.com/keithjasper83/ADR-Master/releases/tag/v0.1.0
