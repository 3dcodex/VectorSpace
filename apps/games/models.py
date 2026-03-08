from django.db import models
from apps.users.models import User

class Game(models.Model):
    GAME_STATUS = [('draft', 'Draft'), ('published', 'Published'), ('archived', 'Archived')]
    PLATFORMS = [('pc', 'PC'), ('web', 'Web'), ('mobile', 'Mobile'), ('console', 'Console')]
    ENGINES = [('unreal', 'Unreal Engine'), ('unity', 'Unity'), ('godot', 'Godot'), ('custom', 'Custom'), ('other', 'Other')]
    developer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='games')
    title = models.CharField(max_length=200)
    description = models.TextField()
    genre = models.CharField(max_length=50)
    platform = models.CharField(max_length=20, choices=PLATFORMS, default='pc')
    engine = models.CharField(max_length=20, choices=ENGINES, default='unity')
    status = models.CharField(max_length=20, choices=GAME_STATUS, default='draft')
    build_file = models.FileField(upload_to='games/', blank=True)
    thumbnail = models.CharField(max_length=255)
    trailer_url = models.URLField(blank=True)
    downloads = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)  # Track page views for recommendations
    rating = models.FloatField(default=0)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(null=True, blank=True)

class GameVersion(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='versions')
    version = models.CharField(max_length=20)
    build_file = models.FileField(upload_to='game_versions/')
    changelog = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class GameReview(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_reviews')
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    helpful_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('game', 'user')

class GameComment(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class FollowDeveloper(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_devs')
    developer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dev_followers')
    followed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('follower', 'developer')

