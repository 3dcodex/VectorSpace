"""
Advanced Search & Discovery Models
Full-text search, trending algorithm, user search history, etc.
"""
from django.db import models
from apps.users.models import User
from apps.marketplace.models import Asset
from apps.games.models import Game


class SearchQuery(models.Model):
    """
    Track user search queries for analytics and trending
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='search_queries')
    query_text = models.CharField(max_length=500)
    search_type = models.CharField(max_length=20, choices=[
        ('assets', 'Assets'),
        ('games', 'Games'),
        ('creators', 'Creators'),
        ('global', 'Global'),
    ])
    
    results_count = models.IntegerField(default=0)
    
    # Filters applied
    filters_applied = models.JSONField(default=dict, help_text="Filters used: category, price_range, rating_min, etc.")
    
    # Engagement
    clicked_result = models.BooleanField(default=False, help_text="User clicked on a search result")
    click_position = models.IntegerField(null=True, blank=True, help_text="Position of clicked result (0-indexed)")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.CharField(max_length=45, blank=True, help_text="User IP for anonymous tracking")
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['query_text', 'search_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.query_text} ({self.search_type})"


class SavedSearch(models.Model):
    """
    User's saved searches with filters for quick re-running
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    
    name = models.CharField(max_length=200)
    search_type = models.CharField(max_length=20, choices=[
        ('assets', 'Assets'),
        ('games', 'Games'),
    ])
    
    # The query
    query_text = models.CharField(max_length=500)
    filters = models.JSONField(default=dict)
    
    # Metadata
    is_public = models.BooleanField(default=False, help_text="Share search with community")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Engagement
    run_count = models.IntegerField(default=0)
    last_run = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-updated_at']
        unique_together = [('user', 'name')]
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class TrendingItem(models.Model):
    """
    Cache of trending items calculated periodically
    """
    ITEM_TYPES = [
        ('asset', 'Asset'),
        ('game', 'Game'),
    ]
    
    item_type = models.CharField(max_length=10, choices=ITEM_TYPES)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, blank=True, related_name='trending_records')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True, related_name='trending_records')
    
    # Trending metrics
    score = models.FloatField(default=0, help_text="Composite trending score")
    
    # Components of score
    views_30d = models.IntegerField(default=0)
    purchases_30d = models.IntegerField(default=0)
    likes_30d = models.IntegerField(default=0)
    rating_avg = models.FloatField(default=0)
    
    # Time period
    calculated_at = models.DateTimeField(auto_now=True)
    period = models.CharField(max_length=20, choices=[
        ('today', 'Today'),
        ('week', 'This Week'),
        ('month', 'This Month'),
        ('all_time', 'All Time'),
    ], default='month')
    
    # Ranking
    ranking = models.IntegerField(default=0, help_text="Position in trending list")
    
    class Meta:
        ordering = ['period', 'ranking']
        unique_together = [('item_type', 'asset', 'period'), ('item_type', 'game', 'period')]
        indexes = [
            models.Index(fields=['period', 'ranking']),
            models.Index(fields=['score', '-calculated_at']),
        ]
    
    def __str__(self):
        if self.asset:
            return f"Trending: {self.asset.title} ({self.period})"
        return f"Trending: {self.game.title} ({self.period})"
    
    def get_item(self):
        return self.asset if self.asset else self.game


class SearchFilter(models.Model):
    """
    Maintain faceted search filters available for each category
    """
    FILTER_TYPES = [
        ('category', 'Category'),
        ('price_range', 'Price Range'),
        ('rating', 'Rating'),
        ('tag', 'Tag'),
        ('format', 'Format'),
        ('creator', 'Creator'),
        ('license', 'License'),
    ]
    
    filter_type = models.CharField(max_length=20, choices=FILTER_TYPES)
    label = models.CharField(max_length=100)  # Display name
    value = models.CharField(max_length=100)  # Actual value to filter by
    
    # For faceted search count
    asset_count = models.IntegerField(default=0)
    game_count = models.IntegerField(default=0)
    
    # Display settings
    icon = models.CharField(max_length=50, blank=True, help_text="Emoji or icon")
    color = models.CharField(max_length=7, blank=True, help_text="Hex color for UI")
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['filter_type', 'order']
        unique_together = [('filter_type', 'value')]
    
    def __str__(self):
        return f"{self.filter_type}: {self.label}"


class SimilarItem(models.Model):
    """
    Pre-calculated similar items for faster recommendations
    """
    source_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='similar_assets')
    
    # Similar items (assets or games)
    similar_asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, blank=True, 
                                       related_name='found_similar_in_assets')
    similar_game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True,
                                      related_name='found_similar_in_games')
    
    # Similarity score (0-1)
    similarity_score = models.FloatField(default=0)
    
    # How similarity was calculated
    matching_tags = models.IntegerField(default=0)
    matching_category = models.BooleanField(default=False)
    collaborator_bought = models.BooleanField(default=False)
    
    # Ranking
    rank = models.IntegerField(default=0)
    
    # Metadata
    calculated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-similarity_score']
        unique_together = [
            ('source_asset', 'similar_asset'),
            ('source_asset', 'similar_game'),
        ]
    
    def __str__(self):
        if self.similar_asset:
            return f"{self.source_asset.title} → {self.similar_asset.title}"
        return f"{self.source_asset.title} → {self.similar_game.title}"
    
    def get_similar_item(self):
        return self.similar_asset if self.similar_asset else self.similar_game


class DiscoveryCard(models.Model):
    """
    Curated discovery cards shown on homepage/marketplace
    (Trending, New, Popular in Category, Recommended)
    """
    CARD_TYPES = [
        ('trending', 'Trending Now'),
        ('new', 'New Releases'),
        ('popular_category', 'Popular in Category'),
        ('staff_pick', 'Staff Picks'),
        ('seasonal', 'Seasonal'),
    ]
    
    card_type = models.CharField(max_length=30, choices=CARD_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Content
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True)
    
    # Display settings
    banner_image = models.CharField(max_length=500, blank=True)
    background_color = models.CharField(max_length=7, blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Time period
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Analytics
    views = models.IntegerField(default=0)
    clicks = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', '-views']
    
    def __str__(self):
        return f"{self.get_card_type_display()} - {self.title}"


class SearchAnalytics(models.Model):
    """
    Daily aggregated search analytics
    """
    date = models.DateField()
    
    total_searches = models.IntegerField(default=0)
    unique_searchers = models.IntegerField(default=0)
    
    # Search results clicked
    total_clicks = models.IntegerField(default=0)
    click_through_rate = models.FloatField(default=0)  # clicks/searches
    
    # Top searches
    top_queries = models.JSONField(default=list)  # [{"query": "3D", "count": 42}, ...]
    
    class Meta:
        ordering = ['-date']
        unique_together = [('date',)]
    
    def __str__(self):
        return f"Search Analytics - {self.date}"
