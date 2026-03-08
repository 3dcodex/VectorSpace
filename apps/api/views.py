from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend

from apps.marketplace.models import Asset
from apps.games.models import Game
from apps.jobs.models import Job, Application
from apps.mentorship.models import MentorProfile
from apps.social.models import Post, Message
from apps.competitions.models import Competition, Submission

from .serializers import (
    AssetSerializer, GameSerializer, JobSerializer,
    ApplicationSerializer, MentorProfileSerializer, PostSerializer,
    MessageSerializer, CompetitionSerializer, SubmissionSerializer
)

# Marketplace ViewSets
class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['asset_type', 'is_free', 'seller']
    search_fields = ['title', 'description', 'tags']
    ordering_fields = ['created_at', 'price', 'downloads', 'rating']
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)
    
    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        self.get_object()
        # Implement purchase logic
        return Response({'status': 'purchased'})

# Game ViewSets
class GameViewSet(viewsets.ModelViewSet):
    queryset = Game.objects.filter(status='published')
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genre', 'developer']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'downloads', 'rating']
    
    def perform_create(self, serializer):
        serializer.save(developer=self.request.user, status='published')

# Job ViewSets
class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.filter(active=True)
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job_type', 'remote', 'recruiter']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at']
    
    def perform_create(self, serializer):
        serializer.save(recruiter=self.request.user)

class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Application.objects.filter(applicant=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

# Mentorship ViewSets
class MentorProfileViewSet(viewsets.ModelViewSet):
    queryset = MentorProfile.objects.filter(available=True)
    serializer_class = MentorProfileSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['mentor__username', 'expertise']
    ordering_fields = ['hourly_rate', 'rating', 'total_sessions']

# Social ViewSets
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'likes_count']
    
    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
    
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        post.likes_count += 1
        post.save()
        return Response({'likes_count': post.likes_count})

class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Message.objects.filter(
            sender=self.request.user
        ) | Message.objects.filter(
            recipient=self.request.user
        )
    
    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

# Competition ViewSets
class CompetitionViewSet(viewsets.ModelViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'category']
    search_fields = ['title', 'description']
    ordering_fields = ['start_date', 'prize_pool']
    
    def perform_create(self, serializer):
        serializer.save(organizer=self.request.user)

class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Submission.objects.filter(participant=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(participant=self.request.user)
