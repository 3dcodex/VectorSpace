# Vector Space: Complete Project Documentation

This document is the canonical technical reference for the current Vector Space application.

## 1. Product Overview

Vector Space is a Django platform for game-development ecosystems where users can:

- Discover and purchase assets
- Build and publish games
- Apply for jobs and recruit talent
- Request and provide mentorship
- Join community discussions and competitions
- Collaborate in workspaces
- Use integrated AI assistant tools

The platform separates public discovery from authenticated dashboard actions.

## 2. Role Architecture

### 2.1 Base and Upgrade Roles

Base role:

- `VECTOR` (default for all new users)

Upgrade roles:

- `CREATOR`
- `DEVELOPER`
- `RECRUITER`
- `MENTOR`

### 2.2 Multi-Role Model

User profiles support:

- `primary_role`: main context shown in dashboard
- `secondary_roles`: additional role capabilities

This allows combinations like:

- Vector + Creator
- Vector + Developer
- Vector + Creator + Developer

### 2.3 Admin/Moderator Behavior

Admin users can operate in two modes:

- Moderator mode: moderation/admin-focused sidebar and tools
- View-as mode: impersonate any role UX (Vector/Creator/Developer/Recruiter/Mentor) from one account

Impersonation is preview-only and stored in:

- `UserProfile.admin_view_as_role`

## 3. Access Model and Route Separation

### 3.1 Public Routes

Public pages are for browsing/discovery and do not require dashboard context:

- `/`
- `/marketplace/`
- `/games/`
- `/jobs/`
- `/mentorship/`
- `/community/`
- `/competitions/`
- `/workspace/`
- `/ai/`

### 3.2 Dashboard Routes

User management/actions and private tooling are under:

- `/dashboard/*`

Examples:

- `/dashboard/marketplace/*`
- `/dashboard/games/*`
- `/dashboard/jobs/*`
- `/dashboard/mentorship/*`
- `/dashboard/social/*`

### 3.3 API Routes

REST API endpoints are namespaced under:

- `/api/v1/*`

## 4. Sidebar System

Sidebar is dynamic and capability-driven.

### 4.1 Grouping

For non-moderator users:

- Core
- Professional Tools
- Collaboration
- Personal

### 4.2 Visibility Rules

Core is visible to all authenticated users.

Professional tools are role-gated:

- Creator: assets/sales/revenue flows
- Developer: game creation/build/version/analytics flows
- Recruiter: jobs/applicants/hiring flows
- Mentor: mentorship requests/sessions/management flows

Moderator mode replaces this with moderation-centric navigation.

## 5. Main App Modules

- `apps.core`: shared models, notifications, moderation, recommendations, portfolio
- `apps.users`: auth, profile, settings, role model
- `apps.dashboard`: authenticated dashboard views and route composition
- `apps.marketplace`: assets, purchases, wishlist, collections, discovery/search
- `apps.games`: game publishing/discovery/reviews
- `apps.jobs`: job postings and applications
- `apps.mentorship`: mentorship requests and sessions
- `apps.social`: feed, comments, follows, messages
- `apps.competitions`: competitions and submissions
- `apps.workspace`: collaboration/workspace tools
- `apps.ai_assistant`: AI assistant chat features
- `apps.api`: DRF serializers/views/endpoints

## 6. Key Data Model Notes

### 6.1 User Profile

Primary profile model:

- `apps.users.models.UserProfile`

Important fields:

- `primary_role`
- `secondary_roles`
- `admin_view_as_role`
- role-specific score counters and profile metadata

### 6.2 Reputation Models

- `apps.users.reputation_models.RoleReputation`
- `apps.users.reputation_models.ServiceFlow`
- `apps.users.reputation_models.Badge`
- `apps.users.reputation_models.UserBadge`
- `apps.users.reputation_models.RoleReview`

## 7. Current UX Capabilities

### 7.1 Vector (base user)

Can access:

- Marketplace
- Games
- Community
- Competitions
- Jobs
- Mentorship
- Messages
- Resume builder
- Workspaces
- AI assistant
- Notifications
- Profile and settings

### 7.2 Role Upgrades

From settings, users can unlock additional role toolsets:

- Creator
- Developer
- Recruiter
- Mentor

### 7.3 Admin View-As Flow

From settings, admins can switch role previews without creating extra accounts.

Options include:

- Moderator mode
- Vector
- Creator
- Developer
- Recruiter
- Mentor

## 8. Developer Setup

### 8.1 Local (venv)

```bash
python -m venv venv
# Windows PowerShell
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 8.2 Docker Compose

```bash
docker-compose up --build
```

Expected services:

- Django web app
- Postgres
- Redis
- Celery worker

## 9. Migration Workflow

Create and apply migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

Check migration state:

```bash
python manage.py showmigrations
```

## 10. Validation and Testing

### 10.1 Framework checks

```bash
python manage.py check
```

### 10.2 Full test suite

```bash
python -m pytest -q
```

### 10.3 Template URL audit

```bash
python scripts/utils/audit_template_urls.py
```

This catches unresolved `{% url %}` names in templates.

## 11. URL and Namespace Conventions

- Always use named routes in templates/views.
- Prefer namespace prefixes (for example, `dashboard:...`, `marketplace:...`).
- Keep public and dashboard actions separated.

## 12. Operational Scripts

Useful scripts currently in the repository include:

- `scripts/utils/audit_template_urls.py`
- `scripts/utils/check_admin_capabilities.py`

## 13. Troubleshooting Guide

### 13.1 `NoReverseMatch`

- Verify route name exists in the target namespace.
- Run template audit script.
- Confirm URL include modules are loaded in `config/urls.py` and dashboard URL aggregator.

### 13.2 Migrations pending

- Run `python manage.py migrate`.
- Restart dev server if browser still shows stale migration banner.

### 13.3 Role UI not matching expectation

- Check user profile fields:
  - `primary_role`
  - `secondary_roles`
  - `admin_view_as_role`
- For admins, ensure moderator mode vs impersonation mode is set as intended.

## 14. Security and Policy Notes

- Admin impersonation is intended for local/dev workflow and UX verification.
- Keep admin credentials secure and unique per environment.
- Review production policy before enabling any elevated preview mode externally.

## 15. Source of Truth

When this file and other docs differ, trust:

1. Current code in `apps/*`
2. Current URL routing in `config/urls.py` and `apps/dashboard/urls/*`
3. Current tests and audit scripts

This file should be updated whenever role logic, route structure, or dashboard behavior changes.
