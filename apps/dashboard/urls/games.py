from django.urls import path
from apps.dashboard.views import games

urlpatterns = [
    path('published/', games.my_games, name='games_my_games'),
    path('publish/', games.publish_game, name='games_publish'),
    path('<int:pk>/edit/', games.edit_game, name='games_edit'),
]
