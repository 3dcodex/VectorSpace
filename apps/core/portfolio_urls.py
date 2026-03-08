"""
Portfolio URL patterns
"""
from django.urls import path
from apps.core import portfolio_views

app_name = 'portfolio'

urlpatterns = [
    # Public portfolio pages
    path('creators/', portfolio_views.portfolio_list, name='list'),
    path('creator/<slug:custom_url>/', portfolio_views.portfolio_detail, name='detail'),
]
