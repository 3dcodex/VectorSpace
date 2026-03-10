from rest_framework import serializers
from apps.users.models import User, UserProfile
from apps.marketplace.models import Asset, Review
from apps.games.models import Game, GameVersion
from apps.jobs.models import Job, Application
from apps.mentorship.models import MentorProfile, Session
from apps.social.models import Post, Comment, Message
from apps.competitions.models import Competition, Submission

# User Serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'bio', 'avatar', 'rating', 'email_verified']
        read_only_fields = ['id', 'email_verified']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = '__all__'

# Marketplace Serializers
class AssetSerializer(serializers.ModelSerializer):
    seller = UserSerializer(read_only=True)
    
    class Meta:
        model = Asset
        fields = '__all__'
        read_only_fields = ['downloads', 'rating', 'created_at', 'updated_at']

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['created_at']

# Game Serializers
class GameSerializer(serializers.ModelSerializer):
    developer = UserSerializer(read_only=True)
    
    class Meta:
        model = Game
        fields = '__all__'
        read_only_fields = ['downloads', 'rating', 'created_at', 'published_at']

class GameVersionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameVersion
        fields = '__all__'
        read_only_fields = ['created_at']

# Job Serializers
class JobSerializer(serializers.ModelSerializer):
    recruiter = UserSerializer(read_only=True)
    
    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ['created_at']

class ApplicationSerializer(serializers.ModelSerializer):
    applicant = UserSerializer(read_only=True)
    job = JobSerializer(read_only=True)
    
    class Meta:
        model = Application
        fields = '__all__'
        read_only_fields = ['applied_at']

# Mentorship Serializers
class MentorProfileSerializer(serializers.ModelSerializer):
    mentor = UserSerializer(read_only=True)
    
    class Meta:
        model = MentorProfile
        fields = '__all__'

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'

# Social Serializers
class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)
    
    class Meta:
        model = Post
        fields = '__all__'
        read_only_fields = ['likes_count', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['created_at']

class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    recipient = UserSerializer(read_only=True)
    
    class Meta:
        model = Message
        fields = '__all__'
        read_only_fields = ['created_at']

# Competition Serializers
class CompetitionSerializer(serializers.ModelSerializer):
    organizer = UserSerializer(read_only=True)
    submissions_count = serializers.IntegerField(source='submissions.count', read_only=True)
    
    class Meta:
        model = Competition
        fields = '__all__'
        read_only_fields = ['created_at']

class SubmissionSerializer(serializers.ModelSerializer):
    participant = UserSerializer(read_only=True)
    votes_count = serializers.IntegerField(source='votes.count', read_only=True)
    
    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['score', 'submitted_at']
