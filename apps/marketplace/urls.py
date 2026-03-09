from django.urls import path, include
from . import views_public

app_name = 'marketplace'

urlpatterns = [
    # Public URLs - Browse and view assets
    path('', views_public.marketplace_list, name='list'),
    path('browse/', views_public.marketplace_list, name='browse'),
    path('<int:pk>/', views_public.asset_detail, name='detail'),
    path('<int:pk>/', views_public.asset_detail, name='asset_detail'),
    path('<int:pk>/purchase/', views_public.purchase_asset, name='purchase'),
    path('webhook/stripe/', views_public.stripe_webhook, name='stripe_webhook'),
    path('payment/success/', views_public.payment_success, name='payment_success'),
    path('payment/cancel/', views_public.payment_cancel, name='payment_cancel'),
    
    # Search & discovery
    path('', include('apps.marketplace.search_urls')),
]
