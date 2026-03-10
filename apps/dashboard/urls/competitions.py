from django.urls import path
from apps.dashboard.views import competitions

urlpatterns = [
    path('my-competitions/', competitions.my_competitions, name='dashboard_competitions_my_competitions'),
    path('my-competitions/', competitions.my_competitions, name='competitions_my_competitions'),
    path('create/', competitions.create_competition, name='dashboard_competitions_create'),
    path('create/', competitions.create_competition, name='competitions_create'),
    path('my-submissions/', competitions.my_submissions, name='dashboard_competitions_my_submissions'),
    path('my-submissions/', competitions.my_submissions, name='competitions_my_submissions'),
    path('<int:pk>/submit/', competitions.submit_entry, name='dashboard_competitions_submit'),
    path('<int:pk>/submit/', competitions.submit_entry, name='competitions_submit'),
    path('submission/<int:pk>/vote/', competitions.vote_submission, name='dashboard_competitions_vote'),
    path('submission/<int:pk>/vote/', competitions.vote_submission, name='competitions_vote'),
]
