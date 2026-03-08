"""
Creator Portfolio Models
Extends User/UserProfile with portfolio-specific features: featured items, achievements, badges, etc.
"""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from apps.users.models import User
from apps.marketplace.models import Asset
from apps.games.models import Game


class CreatorPortfolio(models.Model):
    """
    Enhanced portfolio for creators showcasing their best work.
    One-to-one with User model.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='creator_portfolio')
    
    # Portfolio settings
    is_public = models.BooleanField(default=True, help_text="Make portfolio visible to everyone")
    custom_url = models.SlugField(max_length=100, unique=True, blank=True, help_text="Custom portfolio URL")
    
    # Professional info
    tagline = models.CharField(max_length=200, blank=True, help_text="Short professional tagline")
    specialties = models.JSONField(default=list, help_text="List of specialties/focus areas")
    years_experience = models.IntegerField(default=0)
    
    # Portfolio theme/branding
    cover_image = models.CharField(max_length=500, blank=True)
    primary_color = models.CharField(max_length=7, default='#0db9f2', help_text="Hex color code")
    
    # Stats and analytics
    total_views = models.IntegerField(default=0)
    total_likes = models.IntegerField(default=0)
    total_downloads = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    # Social proof
    featured_by_platform = models.BooleanField(default=False)
    verified_creator = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-total_views']
        indexes = [
            models.Index(fields=['is_public', '-total_views']),
            models.Index(fields=['custom_url']),
        ]
    
    def __str__(self):
        return f"{self.user.username}'s Portfolio"
    
    def save(self, *args, **kwargs):
        # Auto-generate custom URL from username if not set
        if not self.custom_url:
            base_slug = slugify(self.user.username)
            slug = base_slug
            counter = 1
            while CreatorPortfolio.objects.filter(custom_url=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.custom_url = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('portfolio:detail', kwargs={'custom_url': self.custom_url})
    
    @property
    def total_projects(self):
        """Total assets + games published"""
        return self.user.assets.filter(is_active=True).count() + self.user.games.filter(is_active=True).count()
    
    @property
    def average_rating(self):
        """Calculate average rating across all work"""
        # Could be calculated from asset/game ratings
        return self.user.rating


class FeaturedItem(models.Model):
    """
    Items featured on a creator's portfolio (assets or games)
    """
    ITEM_TYPES = [
        ('asset', 'Asset'),
        ('game', 'Game'),
    ]
    
    portfolio = models.ForeignKey(CreatorPortfolio, on_delete=models.CASCADE, related_name='featured_items')
    item_type = models.CharField(max_length=10, choices=ITEM_TYPES)
    
    # Generic foreign keys to assets or games
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, blank=True, related_name='featured_in')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True, blank=True, related_name='featured_in')
    
    # Featured item details
    order = models.IntegerField(default=0, help_text="Display order (lower = earlier)")
    featured_note = models.TextField(blank=True, help_text="Why this work is special")
    is_showcase = models.BooleanField(default=False, help_text="Pin to top of portfolio")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', '-created_at']
        unique_together = [('portfolio', 'asset'), ('portfolio', 'game')]
    
    def __str__(self):
        if self.asset:
            return f"Featured: {self.asset.title}"
        elif self.game:
            return f"Featured: {self.game.title}"
        return "Featured Item"
    
    def get_item(self):
        """Return the actual asset or game object"""
        return self.asset if self.asset else self.game
    
    def get_title(self):
        item = self.get_item()
        return item.title if item else "Untitled"
    
    def get_image(self):
        item = self.get_item()
        if hasattr(item, 'preview_image'):
            return item.preview_image
        elif hasattr(item, 'thumbnail'):
            return item.thumbnail
        return None


class Achievement(models.Model):
    """
    Achievements earned by creators (milestones, badges, etc.)
    """
    ACHIEVEMENT_TYPES = [
        ('milestone', 'Milestone'),
        ('badge', 'Badge'),
        ('award', 'Award'),
        ('certification', 'Certification'),
    ]
    
    portfolio = models.ForeignKey(CreatorPortfolio, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=20, choices=ACHIEVEMENT_TYPES)
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='🏆', help_text="Emoji or icon class")
    color = models.CharField(max_length=7, default='#f59e0b', help_text="Badge color hex code")
    
    # Achievement criteria
    earned_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=True)
    is_rare = models.BooleanField(default=False, help_text="Special/rare achievement")
    
    # Progress tracking (for progressive achievements)
    progress_current = models.IntegerField(default=0)
    progress_target = models.IntegerField(default=1)
    
    class Meta:
        ordering = ['-is_rare', '-earned_at']
    
    def __str__(self):
        return f"{self.portfolio.user.username} - {self.title}"
    
    @property
    def is_completed(self):
        return self.progress_current >= self.progress_target
    
    @property
    def progress_percentage(self):
        if self.progress_target == 0:
            return 100
        return min(100, int((self.progress_current / self.progress_target) * 100))


class PortfolioSection(models.Model):
    """
    Custom sections for organizing portfolio content
    """
    portfolio = models.ForeignKey(CreatorPortfolio, on_delete=models.CASCADE, related_name='sections')
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='📦', help_text="Section icon emoji")
    order = models.IntegerField(default=0)
    is_visible = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
        unique_together = [('portfolio', 'title')]
    
    def __str__(self):
        return f"{self.portfolio.user.username} - {self.title}"


class Testimonial(models.Model):
    """
    Client testimonials and reviews for creator portfolios
    """
    portfolio = models.ForeignKey(CreatorPortfolio, on_delete=models.CASCADE, related_name='testimonials')
    
    # Testimonial content
    author_name = models.CharField(max_length=200)
    author_title = models.CharField(max_length=200, blank=True, help_text="e.g., 'CEO at Company'")
    author_avatar = models.CharField(max_length=500, blank=True)
    
    content = models.TextField(help_text="The testimonial text")
    rating = models.IntegerField(default=5, help_text="Rating out of 5")
    
    # Related work (optional)
    related_asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)
    related_game = models.ForeignKey(Game, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Metadata
    is_featured = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
    
    def __str__(self):
        return f"Testimonial from {self.author_name} for {self.portfolio.user.username}"


class PortfolioAnalytics(models.Model):
    """
    Daily analytics for portfolio views, engagement, etc.
    """
    portfolio = models.ForeignKey(CreatorPortfolio, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    
    # Daily metrics
    views = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    downloads = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Engagement
    avg_time_on_page = models.IntegerField(default=0, help_text="Average seconds spent")
    
    class Meta:
        ordering = ['-date']
        unique_together = [('portfolio', 'date')]
        indexes = [
            models.Index(fields=['portfolio', '-date']),
        ]
    
    def __str__(self):
        return f"{self.portfolio.user.username} - {self.date}"
