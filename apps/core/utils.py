from django.utils.text import slugify
from django.core.mail import send_mail
from django.conf import settings

def generate_unique_filename(instance, filename):
    """Generate unique filename for uploads"""
    ext = filename.split('.')[-1]
    filename = f"{slugify(instance.title)}_{instance.pk}.{ext}"
    return filename

def send_notification_email(user, subject, message):
    """Send notification email to user"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def format_file_size(size_bytes):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def create_notification(user, notification_type, title, message, link=''):
    """
    Create a notification for a user
    
    Args:
        user: User object
        notification_type: Type of notification (see Notification.NOTIFICATION_TYPES)
        title: Notification title
        message: Notification message
        link: Optional link to related content
    
    Returns:
        Notification object
    """
    from apps.core.notifications import Notification
    
    notification = Notification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        link=link
    )
    
    return notification
