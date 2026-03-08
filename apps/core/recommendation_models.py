from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.users.models import User


class UserInteraction(models.Model):
    """Track user interactions with content for recommendation analysis"""
    INTERACTION_TYPES = [
        ('view', 'View'),
        ('click', 'Click'),
        ('download', 'Download'),
        ('purchase', 'Purchase'),
        ('like', 'Like'),
        ('share', 'Share'),
        ('search_result_click', 'Search Result Click'),
    ]
    
    CONTENT_TYPES = [
        ('asset', 'Asset'),
        ('game', 'Game'),
        ('job', 'Job'),
        ('user_profile', 'User Profile'),
        ('post', 'Post'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=30, choices=INTERACTION_TYPES)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_id = models.IntegerField()  # ID of the viewed/interacted content
    duration_seconds = models.IntegerField(null=True, blank=True)  # Time spent
    interaction_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )  # Purchase amount, rating value, etc.
    search_query = models.CharField(max_length=255, blank=True)  # If from search
    referrer_type = models.CharField(max_length=50, blank=True)  # How they found it
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['content_type', 'content_id']),
            models.Index(fields=['interaction_type']),
            models.Index(fields=['user', 'content_type', 'interaction_type']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} - {self.content_type}:{self.content_id}"


class UserPreference(models.Model):
    """User preferences for recommendations"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='recommendation_preferences')
    
    # Content preferences  
    preferred_asset_types = models.JSONField(default=list)  # List of asset types
    preferred_game_genres = models.JSONField(default=list)  # List of game genres
    preferred_job_types = models.JSONField(default=list)   # List of job types
    preferred_software = models.JSONField(default=list)    # Blender, Unity, etc.
    
    # Recommendation settings
    enable_recommendations = models.BooleanField(default=True)
    include_social_signals = models.BooleanField(default=True)  # Use friend activity
    include_trending = models.BooleanField(default=True)       # Show trending items
    max_price_preference = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    
    # Blocked content
    blocked_sellers = models.ManyToManyField(
        User, blank=True, related_name='blocked_by_users'
    )
    blocked_categories = models.JSONField(default=list)
    
    # Privacy settings  
    share_activity_for_recommendations = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - Recommendation Preferences"


class WishlistExtended(models.Model):
    """Extended wishlist for games and other content types (assets use marketplace.Wishlist)"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='extended_wishlist')
    content_type = models.CharField(max_length=20, choices=[
        ('game', 'Game'),
        ('job', 'Job'),  # For saving interesting job posts
    ])
    content_id = models.IntegerField()
    notes = models.TextField(blank=True)  # User notes about why they want it
    priority = models.IntegerField(
        default=3, 
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )  # 1=low, 5=high
    price_alert_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )  # Alert if price drops below this
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'content_type', 'content_id')
        indexes = [
            models.Index(fields=['user', 'content_type']),
            models.Index(fields=['content_type', 'content_id']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - Wishlist - {self.content_type}:{self.content_id}"


class SearchHistory(models.Model):
    """Track search queries for recommendation analysis"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='search_history')
    query = models.CharField(max_length=255)
    search_type = models.CharField(max_length=20, choices=[
        ('asset', 'Asset Search'),
        ('game', 'Game Search'),
        ('job', 'Job Search'),
        ('user', 'User Search'),
        ('general', 'General Search'),
    ])
    results_count = models.IntegerField(default=0)
    clicked_result_id = models.IntegerField(null=True, blank=True)  # Which result they clicked
    clicked_result_position = models.IntegerField(null=True, blank=True)  # Position in results
    filters_used = models.JSONField(default=dict)  # Filters applied during search
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['search_type', 'query']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - Search: '{self.query}'"


class RecommendationScore(models.Model):
    """Cached recommendation scores for performance"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendation_scores')
    content_type = models.CharField(max_length=20, choices=[
        ('asset', 'Asset'),
        ('game', 'Game'),
        ('job', 'Job'),
    ])
    content_id = models.IntegerField()
    score = models.FloatField()
    score_components = models.JSONField(default=dict)  # Breakdown of score calculation
    recommendation_reason = models.CharField(max_length=255)  # "Because you purchased X"
    last_calculated = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'content_type', 'content_id')
        indexes = [
            models.Index(fields=['user', 'content_type', 'score']),
            models.Index(fields=['content_type', 'content_id']),
            models.Index(fields=['last_calculated']),
        ]
        
    def __str__(self):
        return f"{self.user.username} - {self.content_type}:{self.content_id} - {self.score:.2f}"