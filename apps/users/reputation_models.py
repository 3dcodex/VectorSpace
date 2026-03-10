"""
Reputation and Service Flow Tracking Models
Tracks how users interact as providers and consumers
"""
from django.db import models
from django.utils import timezone
from .models import User


class RoleReputation(models.Model):
    """
    Comprehensive reputation tracking for each role
    Automatically calculated based on user activities
    """
    ROLE_CHOICES = [
        ('VECTOR', 'Vector Member'),
        ('PLAYER', 'Player (Legacy)'),
        ('CREATOR', 'Creator'),
        ('DEVELOPER', 'Developer'),
        ('RECRUITER', 'Recruiter'),
        ('MENTOR', 'Mentor'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_reputations')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    
    # Overall reputation score (0-100)
    score = models.FloatField(default=0)
    
    # Service quality metrics
    average_rating = models.FloatField(default=0)
    total_reviews = models.IntegerField(default=0)
    five_star_count = models.IntegerField(default=0)
    
    # Activity metrics
    services_provided = models.IntegerField(default=0)  # Assets sold, games published, etc.
    services_consumed = models.IntegerField(default=0)  # Assets bought, games played, etc.
    
    # Engagement metrics
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    community_engagement = models.IntegerField(default=0)  # Comments, reviews given
    
    # Trust indicators
    verified_badge = models.BooleanField(default=False)
    trust_level = models.IntegerField(default=1, help_text="1-5, based on history and reputation")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ('user', 'role')
        verbose_name = 'Role Reputation'
        verbose_name_plural = 'Role Reputations'
    
    def __str__(self):
        return f"{self.user.username} - {self.role} (Score: {self.score:.1f})"
    
    def update_score(self):
        """Calculate reputation score based on all metrics"""
        # Weighted scoring system
        rating_weight = 0.4
        activity_weight = 0.3
        revenue_weight = 0.2
        engagement_weight = 0.1
        
        # Normalize each metric to 0-100 scale
        rating_score = (self.average_rating / 5.0) * 100 if self.average_rating else 0
        activity_score = min(100, (self.services_provided / 10) * 100)  # Cap at 10 services
        revenue_score = min(100, (float(self.total_revenue) / 1000) * 100)  # Cap at $1000
        engagement_score = min(100, (self.community_engagement / 50) * 100)  # Cap at 50 engagements
        
        self.score = (
            rating_score * rating_weight +
            activity_score * activity_weight +
            revenue_score * revenue_weight +
            engagement_score * engagement_weight
        )
        
        # Update trust level based on score
        if self.score >= 90:
            self.trust_level = 5
        elif self.score >= 75:
            self.trust_level = 4
        elif self.score >= 50:
            self.trust_level = 3
        elif self.score >= 25:
            self.trust_level = 2
        else:
            self.trust_level = 1
        
        self.save()


class ServiceFlow(models.Model):
    """
    Tracks service transactions between users
    Maps the ecosystem: who provides what to whom
    """
    SERVICE_TYPES = [
        ('asset_sale', 'Asset Sale'),
        ('game_download', 'Game Download'),
        ('job_application', 'Job Application'),
        ('mentorship_session', 'Mentorship Session'),
        ('game_review', 'Game Review'),
        ('asset_review', 'Asset Review'),
    ]
    
    # Provider (who offers the service)
    provider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services_provided')
    provider_role = models.CharField(max_length=20)  # CREATOR, DEVELOPER, etc.
    
    # Consumer (who uses the service)
    consumer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='services_consumed')
    consumer_role = models.CharField(max_length=20, default='VECTOR')
    
    # Service details
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPES)
    service_name = models.CharField(max_length=200)  # Asset title, game name, etc.
    
    # Transaction value
    value = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # $0 for free items
    
    # Quality assessment
    rating = models.IntegerField(null=True, blank=True, help_text="1-5 stars")
    review_text = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Service Flow'
        verbose_name_plural = 'Service Flows'
    
    def __str__(self):
        return f"{self.provider.username} → {self.consumer.username}: {self.service_type}"


class Badge(models.Model):
    """
    Achievement badges for platform milestones
    """
    BADGE_TYPES = [
        ('creator', 'Creator'),
        ('developer', 'Developer'),
        ('recruiter', 'Recruiter'),
        ('mentor', 'Mentor'),
        ('community', 'Community'),
        ('achievement', 'Achievement'),
    ]
    
    name = models.CharField(max_length=100)
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Emoji or icon class")
    rarity = models.CharField(max_length=20, choices=[
        ('common', 'Common'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ], default='common')
    
    # Requirements
    required_score = models.IntegerField(default=0)
    required_count = models.IntegerField(default=0, help_text="Required number of actions")
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class UserBadge(models.Model):
    """
    Badges earned by users
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    displayed = models.BooleanField(default=True, help_text="Show on profile")
    
    class Meta:
        unique_together = ('user', 'badge')
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"


class RoleReview(models.Model):
    """
    Role-specific reviews (separate from asset/game reviews)
    E.g., reviewing a recruiter's hiring process, mentor's teaching quality
    """
    ROLE_TYPES = [
        ('RECRUITER', 'Recruiter'),
        ('MENTOR', 'Mentor'),
    ]
    
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_reviews_given')
    reviewed_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_reviews_received')
    role_reviewed = models.CharField(max_length=20, choices=ROLE_TYPES)
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    review_text = models.TextField()
    
    # Specific criteria
    professionalism = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    communication = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    would_recommend = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('reviewer', 'reviewed_user', 'role_reviewed')
        verbose_name = 'Role Review'
        verbose_name_plural = 'Role Reviews'
    
    def __str__(self):
        return f"{self.reviewer.username} reviewed {self.reviewed_user.username} as {self.role_reviewed}"
