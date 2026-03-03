from django.urls import path
from . import views

app_name = 'competitions'

urlpatterns = [
    path('', views.competition_list, name='list'),
    path('create/', views.create_competition, name='create'),
    path('<int:pk>/', views.competition_detail, name='detail'),
    path('<int:pk>/submit/', views.submit_entry, name='submit'),
    path('<int:pk>/leaderboard/', views.leaderboard, name='leaderboard'),
    path('submission/<int:pk>/vote/', views.vote_submission, name='vote'),
]
