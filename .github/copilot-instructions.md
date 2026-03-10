# Vector Space Development Assistant

## Project Context

Vector Space is a Django-based creator ecosystem platform combining marketplace, games, jobs, mentorship, social networking, and competitions with role-based dashboards.

## Tech Stack

- **Framework**: Django 6.0.2, Python 3.12
- **Database**: SQLite (dev), PostgreSQL (production)
- **Real-time**: Django Channels, WebSockets
- **API**: Django REST Framework
- **Frontend**: Django templates, vanilla JavaScript, modern CSS
- **Background Tasks**: Celery, Redis
- **Development**: Docker, pytest

## Architecture Patterns

### URL Structure
- Public browsing: `/marketplace/`, `/games/`, `/jobs/`, etc.
- Authenticated actions: `/dashboard/*` (marketplace, games, jobs sections)
- API endpoints: `/api/v1/*`

### Apps Organization
- `apps.core`: Shared models (notifications, recommendations, portfolios)
- `apps.marketplace`: Asset listings, purchases, collections, search
- `apps.dashboard`: Unified dashboard views for all features
- `apps.users`: Authentication, profiles, settings
- Other apps: games, jobs, social, mentorship, competitions, workspace, ai_assistant

### Role-Based Access
- User roles: `USER`, `CREATOR`, `RECRUITER`, `MENTOR`
- Check role: `request.user.profile.role`
- Permissions via `@login_required` and role checks in views

## Common Development Tasks

### Creating New Features

1. **Models** in appropriate app (e.g., `apps/marketplace/models.py`)
2. **Views** split by access level:
   - Public views: `views_public.py`
   - Dashboard views: move to `apps/dashboard/views/`
3. **URLs** split similarly:
   - Public: `urls.py` in app
   - Dashboard: `dashboard_urls.py`, then include in `apps/dashboard/urls/`
4. **Templates**:
   - Public: `templates/{app}/`
   - Dashboard: `templates/dashboard/`
   - Base templates: `base.html`, `dashboard_base.html`

### Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Running Tests

```bash
pytest
pytest tests/test_specific.py
```

### Creating Admin Users

```bash
python manage.py createsuperuser
# Or use: python make_admin.py
```

## Code Style Conventions

- **Views**: Use function-based views with `@login_required` decorator
- **Models**: Use clear field names, add `__str__` methods, include `created_at`, `updated_at`
- **Forms**: Define in `forms.py`, inherit from `forms.ModelForm`
- **Messages**: Use Django messages framework for user feedback
- **Redirects**: Use named URLs with namespace (e.g., `redirect('dashboard:marketplace_dashboard')`)
- **Query optimization**: Use `select_related()`, `prefetch_related()` for foreign keys

## Common Patterns

### View with Stats
```python
@login_required
def my_view(request):
    assets = Asset.objects.filter(seller=request.user)
    total_count = assets.count()
    total_revenue = Purchase.objects.filter(
        asset__seller=request.user
    ).aggregate(total=Sum('price_paid'))['total'] or 0
    
    context = {
        'assets': assets,
        'total_count': total_count,
        'total_revenue': total_revenue,
    }
    return render(request, 'template.html', context)
```

### URL Namespacing
```python
# In app urls.py
app_name = 'dashboard'

urlpatterns = [
    path('marketplace/', include('apps.dashboard.urls.marketplace')),
]

# In views: redirect('dashboard:marketplace_dashboard')
```

### File Uploads
```python
# Model
file = models.FileField(upload_to='assets/')

# Form handling
if form.is_valid():
    instance = form.save(commit=False)
    instance.user = request.user
    instance.save()
```

## Error Handling

- Check namespace in redirects: `redirect('dashboard:view_name')` not `redirect('view_name')`
- For NoReverseMatch: verify URL namespaces in `urls.py`
- For template errors: check template paths match app structure
- For 404s: verify URL patterns are registered in main `config/urls.py`

## Scripts and Utilities

- `push_sjeff.bat`: Git helper with deletion warnings and a `sjeff` branch default
- `make_admin.py`: Quick admin user creation
- `check_errors.py`: Check for common issues
- `scripts/setup/`: Setup automation scripts
- `scripts/fixes/`: Fix automation scripts

## Best Practices

1. **Always use namespaced URLs** in redirects and links
2. **Check user roles** before dashboard actions
3. **Use Django messages** for user feedback
4. **Optimize queries** with select/prefetch related
5. **Add tests** for new features
6. **Update documentation** when adding major features
7. **Use transactions** for multi-model operations
8. **Validate** user input with Django forms
9. **Log** important operations to `logs/django.log`
10. **Check migrations** after model changes

## Troubleshooting

- **NoReverseMatch**: Check URL namespaces and names
- **Import errors**: Verify `__init__.py` files exist
- **Migration conflicts**: Use `python manage.py migrate --fake-initial`
- **Static files**: Run `python manage.py collectstatic`
- **Permission errors**: Check file upload paths exist
- **Session issues**: Clear browser cookies or run `python manage.py clearsessions`

## Additional Resources

- Full docs: `ALL_DOCUMENTATION.md`
- Django docs: https://docs.djangoproject.com/
- DRF docs: https://www.django-rest-framework.org/
