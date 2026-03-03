# Role-Based Dashboard Architecture

## Overview
Clean separation of dashboards based on user roles with a central router that automatically directs users to their appropriate dashboard.

## Dashboard Routes

| URL | Role | Description |
|-----|------|-------------|
| `/users/dashboard/` | All | Central router - redirects based on role |
| `/users/dashboard/user/` | USER | Regular user dashboard |
| `/users/dashboard/creator/` | CREATOR | Creator dashboard with assets/games stats |
| `/users/dashboard/mentor/` | MENTOR | Mentor dashboard with sessions |
| `/users/dashboard/recruiter/` | RECRUITER | Recruiter dashboard with jobs/applications |

## Dashboard Features

### Creator Dashboard
**Stats:**
- Total Assets
- Total Games
- Total Downloads
- Total Earnings

**Quick Actions:**
- Upload New Asset
- Publish Game

**Recent Content:**
- Recent Assets (last 5)
- Recent Games (last 3)

**Navigation:**
- Overview
- My Assets
- Upload Asset
- My Games
- Publish Game

### Recruiter Dashboard
**Stats:**
- Total Jobs Posted
- Active Jobs
- Total Applications

**Quick Actions:**
- Post New Job

**Recent Content:**
- Recent Job Postings (last 5)
- Recent Applications (last 5)

**Navigation:**
- Overview
- My Jobs
- Post Job

### Mentor Dashboard
**Stats:**
- Total Sessions
- Hourly Rate

**Content:**
- Upcoming Sessions (next 5)
- Mentor Profile Status

**Navigation:**
- Overview
- Mentorship

### User Dashboard
**Features:**
- Quick Links to all platform features
- Marketplace, Games, Jobs, Mentorship
- Role upgrade information

**Navigation:**
- Overview
- Marketplace
- Games
- Community
- Competitions

## Implementation

### Central Router (apps/users/views.py)
```python
@login_required
def dashboard_view(request):
    role = request.user.profile.role
    
    if role == 'CREATOR':
        return redirect('users:creator_dashboard')
    elif role == 'MENTOR':
        return redirect('users:mentor_dashboard')
    elif role == 'RECRUITER':
        return redirect('users:recruiter_dashboard')
    else:
        return redirect('users:user_dashboard')
```

### Role Protection
Each dashboard checks the user's role:
```python
if request.user.profile.role != 'CREATOR':
    return redirect('users:dashboard')
```

## Template Structure
```
templates/users/dashboards/
├── base_dashboard.html       # Base template with sidebar
├── user_dashboard.html        # Regular user
├── creator_dashboard.html     # Creator
├── mentor_dashboard.html      # Mentor
└── recruiter_dashboard.html   # Recruiter
```

## Design Features
✓ Consistent sidebar navigation
✓ Role-specific quick actions
✓ Real-time statistics from database
✓ Empty states for new users
✓ Responsive design
✓ Vector Space theme (dark gradient, #0db9f2 primary)

## Benefits
✓ Clean separation of concerns
✓ Role-specific UX
✓ Scalable architecture
✓ Professional SaaS-like interface
✓ Easy to add new roles
✓ Automatic routing based on role
