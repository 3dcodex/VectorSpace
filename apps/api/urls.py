from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AssetViewSet, GameViewSet, JobViewSet, ApplicationViewSet,
    MentorProfileViewSet, PostViewSet, MessageViewSet,
    CompetitionViewSet, SubmissionViewSet
)

router = DefaultRouter()
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'games', GameViewSet, basename='game')
router.register(r'jobs', JobViewSet, basename='job')
router.register(r'applications', ApplicationViewSet, basename='application')
router.register(r'mentors', MentorProfileViewSet, basename='mentor')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'competitions', CompetitionViewSet, basename='competition')
router.register(r'submissions', SubmissionViewSet, basename='submission')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
]
