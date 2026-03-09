"""
Dashboard URL configuration.
Aggregates all dashboard-related URL patterns from submodules.
"""
from django.urls import path, include

app_name = 'dashboard'

urlpatterns = [
    path('', include('apps.dashboard.urls.overview')),
    path('marketplace/', include('apps.dashboard.urls.marketplace')),
    path('games/', include('apps.dashboard.urls.games')),
    path('jobs/', include('apps.dashboard.urls.jobs')),
    path('competitions/', include('apps.dashboard.urls.competitions')),
    path('social/', include('apps.dashboard.urls.social')),
    path('mentorship/', include('apps.dashboard.urls.mentorship')),
    path('resume/', include('apps.dashboard.urls.resume')),
    path('analytics/', include('apps.dashboard.urls.analytics')),
    path('notifications/', include('apps.dashboard.urls.notifications')),
    path('portfolio/', include('apps.dashboard.urls.portfolio')),
]
