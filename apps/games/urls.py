from django.urls import path
from . import views_public

app_name = 'games'

urlpatterns = [
    # Public URLs - Browse and view games
    path('', views_public.game_list, name='list'),
    path('<int:pk>/', views_public.game_detail, name='detail'),
    path('<int:pk>/download/', views_public.download_game, name='download'),
    path('<int:pk>/review/', views_public.add_review, name='add_review'),
    path('<int:pk>/comment/', views_public.add_comment, name='add_comment'),
]
