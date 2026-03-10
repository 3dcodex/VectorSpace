from django.urls import path
from apps.dashboard.views import overview

urlpatterns = [
    path('', overview.dashboard_overview, name='dashboard_overview'),
    path('', overview.dashboard_overview, name='overview'),
]
