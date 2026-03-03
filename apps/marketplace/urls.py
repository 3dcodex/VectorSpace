from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.marketplace_list, name='list'),
    path('upload/', views.upload_asset, name='upload'),
    path('my-assets/', views.my_assets, name='my_assets'),
    path('asset/<int:pk>/', views.asset_detail, name='asset_detail'),
    path('<int:pk>/', views.asset_detail, name='detail'),
    path('asset/<int:pk>/edit/', views.edit_asset, name='edit_asset'),
    path('asset/<int:pk>/delete/', views.delete_asset, name='delete_asset'),
    path('asset/<int:pk>/purchase/', views.purchase_asset, name='purchase'),
    path('webhook/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),
]
