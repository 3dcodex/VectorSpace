from django.urls import path
from apps.dashboard.views import marketplace

urlpatterns = [
    path('', marketplace.marketplace_dashboard, name='dashboard_marketplace_dashboard'),
    path('', marketplace.marketplace_dashboard, name='marketplace_dashboard'),
    path('browse/', marketplace.browse_marketplace, name='dashboard_marketplace_browse'),
    path('browse/', marketplace.browse_marketplace, name='marketplace_browse'),
    path('assets/', marketplace.my_assets, name='dashboard_marketplace_my_assets'),
    path('assets/', marketplace.my_assets, name='marketplace_my_assets'),
    path('assets/', marketplace.my_assets, name='marketplace_assets'),
    path('upload/', marketplace.upload_asset, name='dashboard_marketplace_upload'),
    path('upload/', marketplace.upload_asset, name='marketplace_upload'),
    path('assets/<int:pk>/edit/', marketplace.edit_asset, name='dashboard_marketplace_edit_asset'),
    path('assets/<int:pk>/edit/', marketplace.edit_asset, name='marketplace_edit_asset'),
    path('assets/<int:pk>/delete/', marketplace.delete_asset, name='dashboard_marketplace_delete_asset'),
    path('assets/<int:pk>/delete/', marketplace.delete_asset, name='marketplace_delete_asset'),
    path('purchases/', marketplace.my_purchases, name='dashboard_marketplace_purchases'),
    path('purchases/', marketplace.my_purchases, name='marketplace_purchases'),
    path('sales/', marketplace.my_sales, name='dashboard_marketplace_sales'),
    path('sales/', marketplace.my_sales, name='marketplace_sales'),
    path('payouts/', marketplace.payouts, name='dashboard_marketplace_payouts'),
    path('payouts/', marketplace.payouts, name='marketplace_payouts'),
    
        # Wishlist URLs
        path('wishlist/', marketplace.my_wishlist, name='dashboard_marketplace_wishlist'),
        path('wishlist/', marketplace.my_wishlist, name='marketplace_wishlist'),
        path('wishlist/add/<int:asset_id>/', marketplace.add_to_wishlist, name='dashboard_marketplace_add_to_wishlist'),
        path('wishlist/add/<int:asset_id>/', marketplace.add_to_wishlist, name='marketplace_add_to_wishlist'),
        path('wishlist/remove/<int:asset_id>/', marketplace.remove_from_wishlist, name='dashboard_marketplace_remove_from_wishlist'),
        path('wishlist/remove/<int:asset_id>/', marketplace.remove_from_wishlist, name='marketplace_remove_from_wishlist'),
    
        # Collection URLs
        path('collections/', marketplace.my_collections, name='dashboard_marketplace_my_collections'),
        path('collections/', marketplace.my_collections, name='marketplace_my_collections'),
        path('collections/create/', marketplace.create_collection, name='dashboard_marketplace_create_collection'),
        path('collections/create/', marketplace.create_collection, name='marketplace_create_collection'),
        path('collections/<str:username>/<slug:slug>/', marketplace.collection_detail, name='dashboard_marketplace_collection_detail'),
        path('collections/<str:username>/<slug:slug>/', marketplace.collection_detail, name='marketplace_collection_detail'),
        path('collections/<str:username>/<slug:slug>/edit/', marketplace.edit_collection, name='dashboard_marketplace_edit_collection'),
        path('collections/<str:username>/<slug:slug>/edit/', marketplace.edit_collection, name='marketplace_edit_collection'),
        path('collections/<str:username>/<slug:slug>/delete/', marketplace.delete_collection, name='dashboard_marketplace_delete_collection'),
        path('collections/<str:username>/<slug:slug>/delete/', marketplace.delete_collection, name='marketplace_delete_collection'),
        path('collections/<int:collection_id>/add/<int:asset_id>/', marketplace.add_to_collection, name='dashboard_marketplace_add_to_collection'),
        path('collections/<int:collection_id>/add/<int:asset_id>/', marketplace.add_to_collection, name='marketplace_add_to_collection'),
            path('collections/<int:collection_id>/remove/<int:asset_id>/', marketplace.remove_from_collection, name='dashboard_marketplace_remove_from_collection'),
            path('collections/<int:collection_id>/remove/<int:asset_id>/', marketplace.remove_from_collection, name='marketplace_remove_from_collection'),
]
