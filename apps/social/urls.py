from django.urls import path
from . import views_public

app_name = 'social'

urlpatterns = [
    # Public URLs - Community and profiles
    path('', views_public.community, name='community'),
    path('post/<int:pk>/', views_public.post_detail, name='post_detail'),
    path('profile/<int:user_id>/', views_public.user_profile, name='profile'),
]
