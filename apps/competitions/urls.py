from django.urls import path
from . import views_public

app_name = 'competitions'

urlpatterns = [
    # Public URLs - Browse competitions
    path('', views_public.competition_list, name='list'),
    path('<int:pk>/', views_public.competition_detail, name='detail'),
    path('<int:pk>/leaderboard/', views_public.leaderboard, name='leaderboard'),
]
