from django.urls import path
from apps.dashboard.views import games

urlpatterns = [
    path('', games.my_games, name='dashboard_games_list'),
    path('', games.my_games, name='games_list'),
    path('my-games/', games.my_games, name='dashboard_games_my_games'),
    path('my-games/', games.my_games, name='games_my_games'),
    path('create/', games.publish_game, name='dashboard_games_create'),
    path('create/', games.publish_game, name='games_create'),
    path('publish/', games.publish_game, name='dashboard_games_publish'),
    path('publish/', games.publish_game, name='games_publish'),
    path('<int:pk>/edit/', games.edit_game, name='dashboard_games_edit'),
    path('<int:pk>/edit/', games.edit_game, name='games_edit'),
]
