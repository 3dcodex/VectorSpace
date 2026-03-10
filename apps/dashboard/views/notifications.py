from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from apps.core.notifications import Notification

@login_required
def notifications(request):
    """List all notifications with pagination"""
    try:
        notifications_qs = Notification.objects.filter(user=request.user).order_by('-created_at')
        unread_count = notifications_qs.filter(read=False).count()
        
        # Add pagination
        paginator = Paginator(notifications_qs, 20)  # 20 notifications per page
        page_number = request.GET.get('page')
        notifications = paginator.get_page(page_number)
        
        return render(request, 'dashboard/notifications.html', {
            'notifications': notifications,
            'unread_count': unread_count
        })
    except Exception as e:
        messages.error(request, 'Error loading notifications. Please try again.')
        return render(request, 'dashboard/notifications.html', {
            'notifications': [],
            'unread_count': 0
        })

@login_required
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    try:
        notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
        if not notification.read:
            notification.mark_as_read()  # Use model method for real-time updates
            messages.success(request, 'Notification marked as read.')
        
        # Redirect to link if available, otherwise back to notifications
        if notification.link:
            return redirect(notification.link)
        return redirect('dashboard:dashboard_notifications')
    except Exception as e:
        messages.error(request, 'Error marking notification as read.')
        return redirect('dashboard:dashboard_notifications')

@login_required
def mark_all_read(request):
    """Mark all notifications as read via AJAX, POST, or GET."""
    try:
        unread_notifications = Notification.objects.filter(user=request.user, read=False)
        count = unread_notifications.count()
        
        if count > 0:
            unread_notifications.update(read=True)
            
            # Send real-time update for count
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f'notifications_{request.user.id}',
                    {
                        'type': 'notification_count_update',
                        'count': 0
                    }
                )
            
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': True, 'count': count})
            messages.success(request, f'Marked {count} notification{"s" if count != 1 else ""} as read.')
        else:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': True, 'count': 0})
            messages.info(request, 'No unread notifications to mark.')
        
        return redirect('dashboard:dashboard_notifications')
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'error': str(e)})
        messages.error(request, 'Error marking notifications as read.')
        return redirect('dashboard:dashboard_notifications')
