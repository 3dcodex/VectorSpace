from django.urls import path, include
from apps.dashboard.views import overview

app_name = 'dashboard'

urlpatterns = [
    # Main dashboard overview
    path('', overview.dashboard_overview, name='overview'),
    path('', overview.dashboard_overview, name='dashboard_overview'),
    
    # Dashboard sections
    path('marketplace/', include('apps.dashboard.urls.marketplace')),
    path('games/', include('apps.dashboard.urls.games')),
    path('jobs/', include('apps.dashboard.urls.jobs')),
    path('competitions/', include('apps.dashboard.urls.competitions')),
    path('social/', include('apps.dashboard.urls.social')),
    path('analytics/', include('apps.dashboard.urls.analytics')),
    path('notifications/', include('apps.dashboard.urls.notifications')),
    path('mentorship/', include('apps.dashboard.urls.mentorship')),
    path('resume/', include('apps.dashboard.urls.resume')),
    path('portfolio/', include('apps.dashboard.urls.portfolio')),
]
