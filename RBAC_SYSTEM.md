# Role-Based Access Control (RBAC) System

## Overview
Clean role system using UserProfile model with automatic profile creation via Django signals.

## Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| USER | Default role | Browse, purchase, participate in community |
| CREATOR | Content creator | Upload assets, publish games, all USER permissions |
| MENTOR | Mentor/Teacher | Offer mentorship sessions, all USER permissions |
| RECRUITER | Hiring manager | Post jobs, all USER permissions |
| ADMIN | Administrator | Full platform access |

## Implementation

### Models (apps/users/models.py)
- `UserProfile.role` - CharField with ROLE_CHOICES
- Auto-created via `post_save` signal on User creation

### Registration (apps/users/forms.py)
- Role selection field added to UserRegistrationForm
- Role saved to profile during user creation

### Access Control Example
```python
@login_required
def upload_asset(request):
    if request.user.profile.role != 'CREATOR':
        messages.error(request, 'Only creators can upload assets.')
        return redirect('users:dashboard')
    # Upload logic...
```

## Setup Instructions

### Run Setup Script
```bash
python setup_roles.py
```

This will:
- Apply migrations
- Create profiles for existing users
- Set default role to USER

### Manual Migration
```bash
python manage.py migrate users
```

## Usage

### Check User Role
```python
if request.user.profile.role == 'CREATOR':
    # Creator-specific logic
```

### Update User Role (Admin)
```python
user.profile.role = 'CREATOR'
user.profile.save()
```

### Registration Flow
1. User fills registration form
2. Selects role (USER, CREATOR, MENTOR, RECRUITER)
3. User created with selected role
4. Profile auto-created via signal
5. Email verification sent

## Protected Views

### Marketplace Upload
- **URL**: `/marketplace/upload/`
- **Required Role**: CREATOR
- **Redirect**: Dashboard with error message

### Future Protected Views
- Job posting → RECRUITER role
- Mentorship sessions → MENTOR role
- Admin panel → ADMIN role

## Admin Panel
- Manage roles at: `/admin/users/userprofile/`
- Change user roles manually
- View role distribution

## Benefits
✓ Clean separation of concerns
✓ Scalable role system
✓ Easy to add new roles
✓ Automatic profile creation
✓ Aligns with SRS requirements
