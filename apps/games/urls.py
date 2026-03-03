from django.urls import path
from . import views

app_name = 'games'

urlpatterns = [
    path('', views.game_list, name='list'),
    path('publish/', views.publish_game, name='publish'),
    path('<int:pk>/', views.game_detail, name='detail'),
    path('<int:pk>/download/', views.download_game, name='download'),
    path('<int:pk>/review/', views.add_review, name='add_review'),
    path('<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('my-games/', views.my_games, name='my_games'),
]
