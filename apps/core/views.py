from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Analytics
from apps.marketplace.models import Asset, Purchase
from apps.games.models import Game
from apps.social.models import Post

@login_required
def analytics_dashboard(request):
    user = request.user
    
    # Get date range (last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Get analytics data
    analytics = Analytics.objects.filter(
        user=user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    
    # Calculate totals
    total_revenue = analytics.aggregate(Sum('revenue'))['revenue__sum'] or 0
    total_downloads = analytics.aggregate(
        total=Sum('asset_downloads') + Sum('game_downloads')
    )['total'] or 0
    total_views = analytics.aggregate(
        total=Sum('profile_views') + Sum('asset_views') + Sum('game_views')
    )['total'] or 0
    
    # Get user content stats
    assets_count = Asset.objects.filter(seller=user).count()
    games_count = Game.objects.filter(developer=user).count()
    posts_count = Post.objects.filter(author=user).count()
    
    # Get recent purchases
    recent_purchases = Purchase.objects.filter(
        asset__seller=user
    ).select_related('buyer', 'asset').order_by('-purchased_at')[:10]
    
    # Get top performing assets
    top_assets = Asset.objects.filter(seller=user).order_by('-downloads', '-rating')[:5]
    
    # Get top performing games
    top_games = Game.objects.filter(developer=user).order_by('-downloads', '-rating')[:5]
    
    context = {
        'analytics': analytics,
        'total_revenue': total_revenue,
        'total_downloads': total_downloads,
        'total_views': total_views,
        'assets_count': assets_count,
        'games_count': games_count,
        'posts_count': posts_count,
        'recent_purchases': recent_purchases,
        'top_assets': top_assets,
        'top_games': top_games,
        'date_range': f'{start_date} to {end_date}',
    }
    
    return render(request, 'core/analytics.html', context)


@login_required
def report_content(request):
    if request.method == 'POST':
        from .models import Report
        from django.contrib import messages
        
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
    from .models import Report, ModerationAction
    
    # Check if user is staff
    if not request.user.is_staff:
        from django.http import HttpResponseForbidden
        return HttpResponseForbidden("You don't have permission to access this page.")
    
    # Get pending reports
    pending_reports = Report.objects.filter(status='pending').order_by('-created_at')
    
    # Get recent moderation actions
    recent_actions = ModerationAction.objects.select_related(
        'moderator', 'target_user'
    ).order_by('-created_at')[:20]
    
    # Get statistics
    from django.db.models import Count
    report_stats = Report.objects.values('status').annotate(count=Count('id'))
    
    context = {
        'pending_reports': pending_reports,
        'recent_actions': recent_actions,
        'report_stats': report_stats,
    }
    
    return render(request, 'core/moderation.html', context)

@login_required
def resolve_report(request, report_id):
    from .models import Report, ModerationAction
    from django.contrib import messages
    from django.utils import timezone
    
    if not request.user.is_staff:
        from django.http import HttpResponseForbidden
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
            from apps.users.models import User
            
            # Get target user based on content type
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


@login_required
def notifications(request):
    """View user notifications"""
    from .models import Notification
    
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:50]
    unread_count = notifications.filter(read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    
    return render(request, 'core/notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    """Mark notification as read"""
    from .models import Notification
    from django.contrib import messages
    
    notification = get_object_or_404(Notification, pk=notification_id, user=request.user)
    notification.read = True
    notification.save()
    
    if notification.link:
        return redirect(notification.link)
    
    return redirect('core:notifications')

@login_required
def mark_all_read(request):
    """Mark all notifications as read"""
    from .models import Notification
    from django.contrib import messages
    
    Notification.objects.filter(user=request.user, read=False).update(read=True)
    messages.success(request, 'All notifications marked as read.')
    
    return redirect('core:notifications')
