from django.db import models
from apps.users.models import User

# Import existing models to keep them

class Report(models.Model):
    REPORT_TYPES = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('harassment', 'Harassment'),
        ('copyright', 'Copyright Violation'),
        ('other', 'Other'),
    ]
    REPORT_STATUS = [
        ('pending', 'Pending'),
        ('reviewing', 'Under Review'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    CONTENT_TYPES = [
        ('post', 'Post'),
        ('comment', 'Comment'),
        ('game', 'Game'),
        ('asset', 'Asset'),
        ('user', 'User'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_id = models.IntegerField()
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='pending')
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_reports')
    moderator_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

class ModerationAction(models.Model):
    ACTION_TYPES = [
        ('warning', 'Warning'),
        ('content_removal', 'Content Removal'),
        ('temporary_ban', 'Temporary Ban'),
        ('permanent_ban', 'Permanent Ban'),
    ]
    
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderation_actions')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    reason = models.TextField()
    report = models.ForeignKey(Report, on_delete=models.SET_NULL, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Analytics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    profile_views = models.IntegerField(default=0)
    asset_views = models.IntegerField(default=0)
    asset_downloads = models.IntegerField(default=0)
    game_views = models.IntegerField(default=0)
    game_downloads = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']
