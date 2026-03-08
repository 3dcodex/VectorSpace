from django.urls import path
from . import views

app_name = 'games_dashboard'

urlpatterns = [
    path('', views.my_games, name='my_games'),
    path('publish/', views.publish_game, name='publish'),
]
