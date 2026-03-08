# Vector Space

Vector Space is a Django-based creator ecosystem platform that combines a public marketplace and community with a role-based dashboard experience.

Users can discover and buy digital assets, publish games, post jobs, join mentorship sessions, participate in competitions, build creator portfolios, and use workspace/AI tools.

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

Windows PowerShell:

```powershell
python -m venv venv
& .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Linux/macOS:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Apply migrations

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

## Testing

Run tests:

```bash
pytest
```

Pytest is configured with Django settings in `pytest.ini` and includes coverage reporting.

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

## License

This repository currently does not define a license file. Add a `LICENSE` if you want explicit usage terms.
