"""Core views - reporting and moderation only"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count

@login_required
def report_content(request):
    """Report inappropriate content"""
    if request.method == 'POST':
        from .models import Report
        
        content_type = request.POST.get('content_type')
        content_id = request.POST.get('content_id')
        report_type = request.POST.get('report_type')
        description = request.POST.get('description')
        
        if all([content_type, content_id, report_type, description]):
            Report.objects.create(
                reporter=request.user,
                content_type=content_type,
                content_id=content_id,
                report_type=report_type,
                description=description
            )
            messages.success(request, 'Report submitted successfully. Our team will review it.')
        else:
            messages.error(request, 'Please fill all required fields.')
        
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
    return render(request, 'core/report.html')

@login_required
def moderation_dashboard(request):
    """Moderation dashboard (staff only)"""
    from .models import Report, ModerationAction
    
    # Check if user is staff
    if not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    # Get pending reports
    pending_reports = Report.objects.filter(status='pending').order_by('-created_at')
    
    # Get recent moderation actions
    recent_actions = ModerationAction.objects.select_related(
        'moderator', 'target_user'
    ).order_by('-created_at')[:20]
    
    # Get statistics
    report_stats = Report.objects.values('status').annotate(count=Count('id'))
    
    context = {
        'pending_reports': pending_reports,
        'recent_actions': recent_actions,
        'report_stats': report_stats,
    }
    
    return render(request, 'core/moderation.html', context)

@login_required
def resolve_report(request, report_id):
    """Resolve a content report (staff only)"""
    from .models import Report, ModerationAction
    
    if not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    report = get_object_or_404(Report, pk=report_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        notes = request.POST.get('notes', '')
        
        report.status = 'resolved'
        report.moderator = request.user
        report.moderator_notes = notes
        report.resolved_at = timezone.now()
        report.save()
        
        if action != 'dismiss':
            # Create moderation action if needed
            target_user = None
            if report.content_type == 'post':
                from apps.social.models import Post
                content = Post.objects.filter(id=report.content_id).first()
                if content:
                    target_user = content.author
            elif report.content_type == 'game':
                from apps.games.models import Game
                content = Game.objects.filter(id=report.content_id).first()
                if content:
                    target_user = content.developer
            elif report.content_type == 'asset':
                from apps.marketplace.models import Asset
                content = Asset.objects.filter(id=report.content_id).first()
                if content:
                    target_user = content.seller
            
            if target_user:
                ModerationAction.objects.create(
                    moderator=request.user,
                    target_user=target_user,
                    action_type=action,
                    reason=notes,
                    report=report
                )
        
        messages.success(request, 'Report resolved successfully.')
        return redirect('core:moderation')
    
    return render(request, 'core/resolve_report.html', {'report': report})


# =============================================================================
# NOTIFICATION SYSTEM VIEWS
# =============================================================================

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator
from .notifications import Notification, NotificationPreference, send_notification
import json

@login_required
@require_http_methods(["GET"])
def notification_center(request):
    """Main notification center view"""
    # Get filter parameters
    filter_type = request.GET.get('type', 'all')
    filter_read = request.GET.get('read', 'all')  # all, read, unread
    page = request.GET.get('page', 1)
    
    # Build query
    notifications = request.user.notifications.all()
    
    if filter_type != 'all':
        notifications = notifications.filter(notification_type=filter_type)
    
    if filter_read == 'read':
        notifications = notifications.filter(read=True)
    elif filter_read == 'unread':
        notifications = notifications.filter(read=False)
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_obj = paginator.get_page(page)
    
    # Get notification types for filter dropdown
    notification_types = Notification.NOTIFICATION_TYPES
    
    # Get unread count
    unread_count = request.user.notifications.filter(read=False).count()
    
    context = {
        'notifications': page_obj,
        'notification_types': notification_types,
        'current_filter_type': filter_type,
        'current_filter_read': filter_read,
        'unread_count': unread_count,
        'page_obj': page_obj,
    }
    
    return render(request, 'core/notification_center.html', context)


@login_required
@require_http_methods(["GET"])
def notification_api_list(request):
    """API endpoint for getting notifications (for real-time updates)"""
    limit = int(request.GET.get('limit', 20))
    offset = int(request.GET.get('offset', 0))
    
    notifications = request.user.notifications.all()[offset:offset + limit]
    
    notifications_data = [
        {
            'id': notification.id,
            'type': notification.notification_type,
            'title': notification.title,
            'message': notification.message,
            'link': notification.link,
            'priority': notification.priority,
            'read': notification.read,
            'created_at': notification.created_at.isoformat(),
            'action_url': notification.action_url,
        }
        for notification in notifications
    ]
    
    unread_count = request.user.notifications.filter(read=False).count()
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count,
        'has_more': (offset + limit) < request.user.notifications.count()
    })


@login_required
@require_POST
def mark_notification_read(request):
    """Mark a notification as read"""
    data = json.loads(request.body)
    notification_id = data.get('notification_id')
    
    try:
        notification = request.user.notifications.get(id=notification_id)
        notification.mark_as_read()
        
        return JsonResponse({
            'success': True,
            'unread_count': request.user.notifications.filter(read=False).count()
        })
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})


@login_required
@require_POST  
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    request.user.notifications.filter(read=False).update(read=True)
    
    return JsonResponse({
        'success': True,
        'unread_count': 0
    })


@login_required
@require_POST
def delete_notification(request):
    """Delete a notification"""
    data = json.loads(request.body)
    notification_id = data.get('notification_id')
    
    try:
        notification = request.user.notifications.get(id=notification_id)
        notification.delete()
        
        return JsonResponse({
            'success': True,
            'unread_count': request.user.notifications.filter(read=False).count()
        })
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})


@login_required
@require_http_methods(["GET", "POST"])
def notification_preferences(request):
    """Manage notification preferences"""
    # Get or create preferences
    preferences, created = NotificationPreference.objects.get_or_create(
        user=request.user,
        defaults={
            'email_notifications': True,
            'push_notifications': True,
            'marketplace_notifications': True,
            'social_notifications': True,
            'job_notifications': True,
            'mentorship_notifications': True,
            'system_notifications': True,
        }
    )
    
    if request.method == 'POST':
        # Update preferences
        data = json.loads(request.body)
        
        for field in ['email_notifications', 'push_notifications', 'marketplace_notifications',
                     'social_notifications', 'job_notifications', 'mentorship_notifications',
                     'system_notifications']:
            if field in data:
                setattr(preferences, field, data[field])
        
        preferences.save()
        
        return JsonResponse({'success': True, 'message': 'Preferences updated successfully'})
    
    # GET request - return current preferences
    preferences_data = {
        'email_notifications': preferences.email_notifications,
        'push_notifications': preferences.push_notifications,
        'marketplace_notifications': preferences.marketplace_notifications,
        'social_notifications': preferences.social_notifications,
        'job_notifications': preferences.job_notifications,
        'mentorship_notifications': preferences.mentorship_notifications,
        'system_notifications': preferences.system_notifications,
    }
    
    if request.headers.get('accept') == 'application/json':
        return JsonResponse({'preferences': preferences_data})
    
    return render(request, 'core/notification_preferences.html', {'preferences': preferences})


@login_required
@require_http_methods(["GET"])
def notification_widget(request):
    """Get recent notifications for widget display"""
    limit = int(request.GET.get('limit', 5))
    notifications = request.user.notifications.filter(read=False)[:limit]
    
    notifications_data = [
        {
            'id': notification.id,
            'type': notification.notification_type,
            'title': notification.title,
            'message': notification.message[:100] + '...' if len(notification.message) > 100 else notification.message,
            'link': notification.link,
            'priority': notification.priority,
            'created_at': notification.created_at.isoformat(),
            'action_url': notification.action_url,
        }
        for notification in notifications
    ]
    
    unread_count = request.user.notifications.filter(read=False).count()
    
    return JsonResponse({
        'notifications': notifications_data,
        'unread_count': unread_count
    })


# Demo/Testing functions (remove in production)
@login_required
@require_POST
def send_test_notification(request):
    """Send a test notification for development/testing"""
    if not request.user.is_staff:  # Only allow staff to send test notifications
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    data = json.loads(request.body)
    target_user_id = data.get('user_id', request.user.id)
    notification_type = data.get('type', 'system')
    title = data.get('title', 'Test Notification')
    message = data.get('message', 'This is a test notification from Vector Space.')
    
    from apps.users.models import User
    try:
        target_user = User.objects.get(id=target_user_id)
        notification = send_notification(
            user=target_user,
            notification_type=notification_type,
            title=title,
            message=message,
            link='/dashboard/notifications/',
            priority='normal'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Test notification sent',
            'notification_id': notification.id if notification else None
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
