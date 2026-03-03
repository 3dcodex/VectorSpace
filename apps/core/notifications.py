from django.db import models
from apps.users.models import User

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('purchase', 'Purchase'),
        ('review', 'Review'),
        ('comment', 'Comment'),
        ('message', 'Message'),
        ('follow', 'Follow'),
        ('job_application', 'Job Application'),
        ('mentorship_request', 'Mentorship Request'),
        ('competition_submission', 'Competition Submission'),
        ('payment', 'Payment'),
        ('moderation', 'Moderation'),
        ('system', 'System'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
