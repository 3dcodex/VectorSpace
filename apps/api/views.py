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
    
    def get_queryset(self):
        """Filter assets by ownership for edit/delete operations"""
        if self.action in ['update', 'partial_update', 'destroy']:
            return Asset.objects.filter(seller=self.request.user)
        return Asset.objects.all()
    
    def perform_create(self, serializer):
        """Only CREATOR role can create assets"""
        if not self.request.user.profile.is_creator():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Creator role required to upload assets.')
        serializer.save(seller=self.request.user)
    
    def perform_update(self, serializer):
        """Only creator owner can edit"""
        if not self.request.user.profile.is_creator():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Creator role required to edit assets.')

        asset = self.get_object()
        if asset.seller != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only edit your own assets.')
        serializer.save()
    
    def perform_destroy(self, instance):
        """Only creator owner can delete"""
        if not self.request.user.profile.is_creator():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Creator role required to delete assets.')

        if instance.seller != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only delete your own assets.')
        instance.delete()
    
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
    
    def get_queryset(self):
        """Filter games by ownership for edit/delete operations"""
        if self.action in ['update', 'partial_update', 'destroy']:
            return Game.objects.filter(developer=self.request.user)
        return Game.objects.filter(status='published')
    
    def perform_create(self, serializer):
        """Only DEVELOPER role can publish games"""
        if not self.request.user.profile.is_developer():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Developer role required to publish games.')
        serializer.save(developer=self.request.user, status='published')
    
    def perform_update(self, serializer):
        """Only developer owner can edit"""
        if not self.request.user.profile.is_developer():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Developer role required to edit games.')

        game = self.get_object()
        if game.developer != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only edit your own games.')
        serializer.save()
    
    def perform_destroy(self, instance):
        """Only developer owner can delete"""
        if not self.request.user.profile.is_developer():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Developer role required to delete games.')

        if instance.developer != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only delete your own games.')
        instance.delete()

# Job ViewSets
class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.filter(active=True)
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['job_type', 'remote', 'recruiter']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        """Filter jobs by ownership for edit/delete operations"""
        if self.action in ['update', 'partial_update', 'destroy']:
            return Job.objects.filter(recruiter=self.request.user)
        return Job.objects.filter(active=True)
    
    def perform_create(self, serializer):
        """Only RECRUITER role can post jobs"""
        if not self.request.user.profile.is_recruiter():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Recruiter role required to post jobs.')
        serializer.save(recruiter=self.request.user)
    
    def perform_update(self, serializer):
        """Only recruiter owner can edit"""
        if not self.request.user.profile.is_recruiter():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Recruiter role required to edit jobs.')

        job = self.get_object()
        if job.recruiter != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only edit your own job postings.')
        serializer.save()
    
    def perform_destroy(self, instance):
        """Only recruiter owner can delete"""
        if not self.request.user.profile.is_recruiter():
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Recruiter role required to delete jobs.')

        if instance.recruiter != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only delete your own job postings.')
        instance.delete()

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
    
    def get_queryset(self):
        """Filter competitions by ownership for edit/delete operations"""
        if self.action in ['update', 'partial_update', 'destroy']:
            return Competition.objects.filter(organizer=self.request.user)
        return Competition.objects.all()
    
    def perform_create(self, serializer):
        """Only staff or professional-role users can create competitions"""
        if not (self.request.user.is_staff or self.request.user.profile.has_professional_role()):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Professional role required to organize competitions.')
        serializer.save(organizer=self.request.user)
    
    def perform_update(self, serializer):
        """Only professional organizer can edit"""
        if not (self.request.user.is_staff or self.request.user.profile.has_professional_role()):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Professional role required to edit competitions.')

        competition = self.get_object()
        if competition.organizer != self.request.user and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only edit competitions you organize.')
        serializer.save()
    
    def perform_destroy(self, instance):
        """Only professional organizer can delete"""
        if not (self.request.user.is_staff or self.request.user.profile.has_professional_role()):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('Professional role required to delete competitions.')

        if instance.organizer != self.request.user and not self.request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied('You can only delete competitions you organize.')
        instance.delete()

class SubmissionViewSet(viewsets.ModelViewSet):
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Submission.objects.filter(participant=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(participant=self.request.user)
