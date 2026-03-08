from django.urls import path
from . import views

app_name = 'marketplace_dashboard'

urlpatterns = [
    path('', views.my_assets, name='my_assets'),
    path('upload/', views.upload_asset, name='upload'),
    path('<int:pk>/edit/', views.edit_asset, name='edit'),
    path('<int:pk>/delete/', views.delete_asset, name='delete'),
]
