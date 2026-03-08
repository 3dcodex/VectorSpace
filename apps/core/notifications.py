from django.db import models
from apps.users.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


def _safe_group_send(group_name, payload):
    """Best-effort channel send that never breaks core notification flow."""
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            return False
        async_to_sync(channel_layer.group_send)(group_name, payload)
        return True
    except Exception:
        return False

class NotificationPreference(models.Model):
    """User preferences for different types of notifications"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    # Specific notification type preferences
    marketplace_notifications = models.BooleanField(default=True)  # purchases, reviews, new assets
    social_notifications = models.BooleanField(default=True)       # follows, comments, likes
    job_notifications = models.BooleanField(default=True)          # applications, offers
    mentorship_notifications = models.BooleanField(default=True)   # requests, sessions
    system_notifications = models.BooleanField(default=True)       # maintenance, updates
    
    def __str__(self):
        return f"{self.user.username} - Notification Preferences"

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        # Marketplace notifications
        ('purchase', 'Purchase'),
        ('review', 'Review'),
        ('asset_approved', 'Asset Approved'),
        ('asset_rejected', 'Asset Rejected'),
        ('price_change', 'Price Change'),
        
        # Social notifications  
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('like', 'Like'),
        ('mention', 'Mention'),
        
        # Job related
        ('job_application', 'Job Application'),
        ('job_offer', 'Job Offer'),
        
        # Mentorship
        ('mentorship_request', 'Mentorship Request'),
        ('session_scheduled', 'Session Scheduled'),
        
        # Competitions
        ('competition_submission', 'Competition Submission'),
        ('competition_result', 'Competition Result'),
        
        # System
        ('payment', 'Payment'),
        ('moderation', 'Moderation'),
        ('system', 'System'),
        ('welcome', 'Welcome'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=500, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='normal')
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Additional fields for better organization
    related_object_id = models.IntegerField(null=True, blank=True)  # ID of related object
    related_object_type = models.CharField(max_length=50, blank=True)  # Type of related object
    action_url = models.CharField(max_length=500, blank=True)  # URL for primary action
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'read']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['notification_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"

    def mark_as_read(self):
        """Mark notification as read and update real-time count"""
        if not self.read:
            self.read = True
            self.save()

            # Best-effort real-time update to user
            _safe_group_send(
                f'notifications_{self.user.id}',
                {
                    'type': 'notification_count_update',
                    'count': self.user.notifications.filter(read=False).count()
                }
            )


def send_notification(user, notification_type, title, message, link='', priority='normal', 
                     related_object_id=None, related_object_type='', action_url=''):
    """
    Send a notification to a user with real-time delivery
    
    Args:
        user: User object to send notification to
        notification_type: Type of notification (must be in NOTIFICATION_TYPES)
        title: Short title for the notification
        message: Detailed notification message  
        link: Optional link for the notification
        priority: Priority level (low, normal, high, urgent)
        related_object_id: ID of related object
        related_object_type: Type of related object
        action_url: URL for primary action
    
    Returns:
        Notification instance or None if filtered out
    """
    
    # Validate notification_type with safe fallback.
    valid_types = [choice[0] for choice in Notification.NOTIFICATION_TYPES]
    if notification_type not in valid_types:
        notification_type = 'system'
    
    # Check user preferences
    prefs = getattr(user, 'notification_preferences', None)
    if prefs:
        # Check if user wants this type of notification
        if notification_type in ['purchase', 'review', 'asset_approved', 'price_change'] and not prefs.marketplace_notifications:
            return None
        elif notification_type in ['comment', 'follow', 'like', 'mention'] and not prefs.social_notifications:
            return None
        elif notification_type in ['job_application', 'job_offer'] and not prefs.job_notifications:
            return None
        elif notification_type in ['mentorship_request', 'session_scheduled'] and not prefs.mentorship_notifications:
            return None
        elif notification_type in ['system', 'welcome'] and not prefs.system_notifications:
            return None
    
    # Persist notification first; websocket delivery is optional.
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link,
        priority=priority,
        related_object_id=related_object_id,
        related_object_type=related_object_type,
        action_url=action_url
    )

    notification_data = {
        'id': notification.id,
        'type': notification.notification_type,
        'title': notification.title,
        'message': notification.message,
        'link': notification.link,
        'priority': notification.priority,
        'created_at': notification.created_at.isoformat(),
        'action_url': notification.action_url,
    }

    _safe_group_send(
        f'notifications_{user.id}',
        {
            'type': 'notification_message',
            'notification': notification_data
        }
    )

    _safe_group_send(
        f'notifications_{user.id}',
        {
            'type': 'notification_count_update',
            'count': user.notifications.filter(read=False).count()
        }
    )

    return notification


def send_bulk_notification(users, notification_type, title, message, link='', priority='normal',
                          related_object_id=None, related_object_type='', action_url=''):
    """Send notification to multiple users efficiently"""
    notifications = []
    
    for user in users:
        notification = send_notification(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
            priority=priority,
            related_object_id=related_object_id,
            related_object_type=related_object_type,
            action_url=action_url
        )
        if notification:
            notifications.append(notification)
    
    return notifications
