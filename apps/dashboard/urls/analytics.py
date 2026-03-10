from django.urls import path
from apps.dashboard.views import analytics

urlpatterns = [
    path('', analytics.analytics_dashboard, name='dashboard_analytics'),
    path('', analytics.analytics_dashboard, name='analytics'),
]
