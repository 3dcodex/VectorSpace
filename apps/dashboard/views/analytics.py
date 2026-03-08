from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta
from apps.core.models import Analytics
from apps.marketplace.models import Asset, Purchase
from apps.games.models import Game
from apps.social.models import Post

@login_required
def analytics_dashboard(request):
    """User analytics dashboard"""
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
    recent_purchases = Purchase.objects.filter(asset__seller=user).order_by('-purchased_at')[:10]
    
    context = {
        'analytics': analytics,
        'total_revenue': total_revenue,
        'total_downloads': total_downloads,
        'total_views': total_views,
        'assets_count': assets_count,
        'games_count': games_count,
        'posts_count': posts_count,
        'recent_purchases': recent_purchases,
    }
    
    return render(request, 'core/analytics.html', context)
