# Vector Space

Vector Space is a Django-based creator ecosystem platform that combines a public marketplace and community with a role-based dashboard experience.

Users can discover and buy digital assets, publish games, post jobs, join mentorship sessions, participate in competitions, build creator portfolios, and use workspace/AI tools.

## Role System (Vector Model)

- Base role: `VECTOR` (every new account starts here)
- Upgrade roles: `CREATOR`, `DEVELOPER`, `RECRUITER`, `MENTOR`
- Multi-role support:
	- `primary_role` controls main dashboard context
	- `secondary_roles` unlock additional toolsets

### Dynamic Sidebar

The dashboard sidebar expands based on user capabilities and is grouped for UX:

- `Core`: Dashboard, Marketplace, Games, Community, Competitions, Jobs, Mentorship
- `Professional Tools`: Role-specific tools (assets, games, hiring, mentorship management)
- `Collaboration`: Messages, Workspaces
- `Personal`: AI Assistant, Notifications, My Profile, Settings, Resume Builder

### Admin Role Impersonation

Admins/moderators can preview UX for any role from one account:

- Go to `Dashboard -> Settings -> Admin Tools`
- Use **View As Role** to impersonate `VECTOR`, `CREATOR`, `DEVELOPER`, `RECRUITER`, or `MENTOR`
- Select **Moderator Mode** to return to moderation/admin UX

This impersonation does not require creating multiple test accounts.

## Core Modules

- `apps.marketplace`: Asset listings, uploads, purchases, wishlist, collections, search/discovery
- `apps.games`: Game publishing and discovery
- `apps.jobs`: Job posting and applications
- `apps.mentorship`: Mentor listing and session booking
- `apps.social`: Community feed and messaging
- `apps.competitions`: Competition management and submissions
- `apps.dashboard`: Unified user dashboard sections
- `apps.workspace`: Workspace/project features
- `apps.ai_assistant`: AI assistant routes/views
- `apps.api`: REST API endpoints (`/api/v1/`)
- `apps.core`: Shared models, notifications, recommendations, moderation, portfolio

## Tech Stack

- Python 3.12
- Django
- Django REST Framework
- Channels (WebSocket support)
- SQLite for local development (default)
- Optional Postgres + Redis + Celery via Docker Compose

## Quick Start (Local)

### 1. Clone and enter project

```bash
git clone https://github.com/3dcodex/VectorSpace.git
cd VectorSpace
```

### 2. Create virtual environment and install dependencies

#### Windows (PowerShell)

```powershell
python -m venv venv
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### macOS

**Prerequisites**: Ensure Python 3.12+ is installed. Install via Homebrew if needed:

```bash
brew install python@3.12
```

**Setup**:

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
pip install "Django>=4.2,<5.0"
pip install -r requirements.txt
```

**Database migration setup**:

```bash
python manage.py makemigrations
python manage.py migrate
```

The default development database is SQLite, so no separate database server is required for local development. If you switch to PostgreSQL, install the local database dependencies first and then run the same migration commands.

**macOS-specific notes**:
- If you encounter SSL certificate errors, run: `/Applications/Python\ 3.12/Install\ Certificates.command`
- For Pillow installation issues, install image libraries: `brew install libjpeg libpng`
- For PostgreSQL support and migration tooling (optional), install: `brew install postgresql libpq`

#### Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Linux-specific notes**:
- For Pillow and other image support: `sudo apt-get install python3-dev libjpeg-dev zlib1g-dev`
- For PostgreSQL support: `sudo apt-get install libpq-dev`

### 3. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

```bash
python manage.py migrate
```

### 4. Create admin user (optional)

```bash
python manage.py createsuperuser
```

### 5. Run development server

```bash
python manage.py runserver
```

Open: `http://127.0.0.1:8000/`

## Quick Start (Docker Compose)

**Prerequisites**:
- **Windows/macOS**: Install [Docker Desktop](https://www.docker.com/products/docker-desktop)
- **Linux**: Install Docker Engine and Docker Compose

**Run**:

```bash
docker-compose up --build
```

Services from `docker-compose.yml`:

- `web`: Django app on port `8000`
- `db`: Postgres on port `5432`
- `redis`: Redis on port `6379`
- `celery`: Background worker

## Important Routes

- Home: `/`
- Admin: `/admin/`
- Auth: `/auth/`
- Dashboard: `/dashboard/`
- Marketplace: `/marketplace/`
- Games: `/games/`
- Jobs: `/jobs/`
- Mentorship: `/mentorship/`
- Community: `/community/`
- Competitions: `/competitions/`
- Workspace: `/workspace/`
- AI Assistant: `/ai/`
- API: `/api/v1/`

### Public vs Dashboard Separation

- Public discovery pages remain under public routes:
	- `/marketplace/`, `/games/`, `/jobs/`, `/mentorship/`, `/community/`, `/competitions/`
- User-specific actions and management stay under dashboard routes:
	- `/dashboard/*`

## Testing

Run tests:

```bash
python -m pytest -q
```

Pytest is configured with Django settings in `pytest.ini` and includes coverage reporting.

Optional URL audit (template URL tag validation):

```bash
python scripts/utils/audit_template_urls.py
```

## Project Structure

```text
config/                Django project settings and URL routing
apps/                  Django apps by domain
templates/             HTML templates
static/                CSS, JS, images
media/                 Uploaded media
tests/                 Test suite
ALL_DOCUMENTATION.md   Consolidated extended project documentation
```

## Documentation

- Primary docs landing page: `README.md` (this file)
- Extended docs: `ALL_DOCUMENTATION.md`

## Notes for Development

- Default local database is SQLite (`db.sqlite3`).
- Channels fallback to in-memory layer when `channels_redis` is not available.
- Logging output is written to `logs/django.log` and console.
- `DEBUG=True` is enabled in development settings.

## Model Context Protocol (MCP)

The Model Context Protocol (MCP) is an open standard that defines how applications share context with large language models (LLMs). MCP provides a standardized way to connect AI models to different data sources and tools, enabling them to work together more effectively.

### MCP in Vector Space

This project uses MCP to extend the capabilities of the Copilot coding agent by connecting it to:

- Project-specific tools and services
- Custom data sources and APIs
- Development automation scripts
- Testing and debugging utilities

### MCP Configuration

MCP servers can be defined through:

- **JSON MCP Configuration**: Define MCP server connections in `.mcp.json` or similar configuration files
- **Custom Agents**: Create specialized agents with domain-specific knowledge and tool access

### Custom Agents

This project includes a **Vector Space Development Assistant** configured in `.github/copilot-instructions.md`. This custom agent provides:

- Django and Vector Space architecture guidance
- Role-based access patterns and URL namespacing best practices
- Common development patterns and troubleshooting
- Project-specific code generation and refactoring

The assistant automatically loads when you work in this repository with GitHub Copilot enabled.

Custom agents can be configured to:

- Access project-specific documentation
- Execute domain-specific commands
- Integrate with external services
- Provide specialized code generation and refactoring capabilities

For more information:
- [MCP Configuration Guide](https://modelcontextprotocol.io/docs)
- [Writing Custom Agents](https://docs.github.com/en/copilot/customizing-copilot/creating-custom-agents)

## License

This project is licensed under the MIT License. See `LICENSE` for full terms.
