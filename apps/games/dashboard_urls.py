from django.urls import path
from . import views_dashboard

app_name = 'games_dashboard'

urlpatterns = [
    path('', views_dashboard.my_games, name='my_games'),
]
