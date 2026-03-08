"""
Search URL patterns
"""
from django.urls import path
from apps.marketplace import search_views

urlpatterns = [
    # Search pages
    path('search/', search_views.advanced_search, name='search'),
    path('trending/', search_views.trending_items, name='trending'),
    path('<int:asset_id>/similar/', search_views.similar_to_asset, name='similar'),
    
    # AJAX endpoints
    path('api/suggestions/', search_views.search_suggestions, name='suggestions'),
    
    # Dashboard search management
    path('dashboard/searches/', search_views.my_searches, name='my_searches'),
    path('dashboard/save-search/', search_views.save_search, name='save_search'),
    path('dashboard/delete-search/<int:search_id>/', search_views.delete_saved_search, name='delete_saved_search'),
    path('dashboard/run-search/<int:search_id>/', search_views.run_saved_search, name='run_saved_search'),
]
