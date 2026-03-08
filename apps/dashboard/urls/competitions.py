from django.urls import path
from apps.dashboard.views import competitions

urlpatterns = [
    path('my-competitions/', competitions.my_competitions, name='competitions_my_competitions'),
    path('create/', competitions.create_competition, name='competitions_create'),
    path('my-submissions/', competitions.my_submissions, name='competitions_my_submissions'),
    path('<int:pk>/submit/', competitions.submit_entry, name='competitions_submit'),
    path('submission/<int:pk>/vote/', competitions.vote_submission, name='competitions_vote'),
]
