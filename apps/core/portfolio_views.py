"""
Portfolio views for creator portfolio pages and management
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q, Sum, Avg
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator

from apps.core.portfolio_models import (
    CreatorPortfolio, FeaturedItem, Testimonial
)
from apps.marketplace.models import Asset
from apps.games.models import Game


# Public portfolio views

def portfolio_detail(request, custom_url):
    """
    Public view of a creator's portfolio
    """
    portfolio = get_object_or_404(CreatorPortfolio, custom_url=custom_url, is_public=True)
    
    # Increment view count
    portfolio.total_views += 1
    portfolio.save(update_fields=['total_views'])
    
    # Get featured items
    featured_items = portfolio.featured_items.select_related('asset', 'game').all()
    
    # Get achievements (visible only)
    achievements = portfolio.achievements.filter(is_visible=True)[:12]
    
    # Get all work (assets + games)
    assets = Asset.objects.filter(creator=portfolio.user, is_active=True).order_by('-created_at')[:12]
    games = Game.objects.filter(creator=portfolio.user, is_active=True).order_by('-created_at')[:12]
    
    # Get testimonials
    testimonials = portfolio.testimonials.filter(is_approved=True)[:6]
    
    # Portfolio sections
    sections = portfolio.sections.filter(is_visible=True)
    
    # Check if viewing own portfolio
    is_owner = request.user.is_authenticated and request.user == portfolio.user
    
    context = {
        'portfolio': portfolio,
        'featured_items': featured_items,
        'achievements': achievements,
        'assets': assets,
        'games': games,
        'testimonials': testimonials,
        'sections': sections,
        'is_owner': is_owner,
    }
    
    return render(request, 'core/portfolio_detail.html', context)


def portfolio_list(request):
    """
    Browse all public creator portfolios
    """
    portfolios = CreatorPortfolio.objects.filter(is_public=True).select_related('user')
    
    # Search
    search_query = request.GET.get('q', '')
    if search_query:
        portfolios = portfolios.filter(
            Q(user__username__icontains=search_query) |
            Q(tagline__icontains=search_query) |
            Q(specialties__icontains=search_query)
        )
    
    # Filter by specialty
    specialty = request.GET.get('specialty', '')
    if specialty:
        portfolios = portfolios.filter(specialties__contains=[specialty])
    
    # Sort
    sort_by = request.GET.get('sort', 'views')
    sort_options = {
        'views': '-total_views',
        'recent': '-updated_at',
        'rating': '-user__rating',
        'projects': '-total_views',  # Temporary, can add computed field
    }
    portfolios = portfolios.order_by(sort_options.get(sort_by, '-total_views'))
    
    # Pagination
    paginator = Paginator(portfolios, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'specialty': specialty,
        'sort_by': sort_by,
    }
    
    return render(request, 'core/portfolio_list.html', context)


# Dashboard portfolio management

@login_required
def my_portfolio(request):
    """
    Creator's own portfolio dashboard
    """
    portfolio, created = CreatorPortfolio.objects.get_or_create(user=request.user)
    
    # Get all related data
    featured_items = portfolio.featured_items.select_related('asset', 'game').all()
    achievements = portfolio.achievements.all()
    testimonials = portfolio.testimonials.all()
    sections = portfolio.sections.all()
    
    # Recent analytics (last 30 days)
    from datetime import datetime, timedelta
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    recent_analytics = portfolio.analytics.filter(date__gte=thirty_days_ago)
    
    # Calculate totals
    total_views_30d = recent_analytics.aggregate(Sum('views'))['views__sum'] or 0
    total_revenue_30d = recent_analytics.aggregate(Sum('revenue'))['revenue__sum'] or 0
    
    # All available items to feature
    available_assets = Asset.objects.filter(creator=request.user, is_active=True).exclude(
        id__in=featured_items.filter(asset__isnull=False).values_list('asset_id', flat=True)
    )
    available_games = Game.objects.filter(creator=request.user, is_active=True).exclude(
        id__in=featured_items.filter(game__isnull=False).values_list('game_id', flat=True)
    )
    
    context = {
        'portfolio': portfolio,
        'featured_items': featured_items,
        'achievements': achievements,
        'testimonials': testimonials,
        'sections': sections,
        'total_views_30d': total_views_30d,
        'total_revenue_30d': total_revenue_30d,
        'available_assets': available_assets,
        'available_games': available_games,
    }
    
    return render(request, 'dashboard/portfolio/my_portfolio.html', context)


@login_required
def edit_portfolio_settings(request):
    """
    Edit portfolio settings and basic info
    """
    portfolio, created = CreatorPortfolio.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # Update portfolio settings
        portfolio.is_public = request.POST.get('is_public') == 'on'
        portfolio.tagline = request.POST.get('tagline', '')
        portfolio.years_experience = int(request.POST.get('years_experience', 0))
        portfolio.cover_image = request.POST.get('cover_image', '')
        portfolio.primary_color = request.POST.get('primary_color', '#0db9f2')
        
        # Handle specialties (comma-separated)
        specialties_raw = request.POST.get('specialties', '')
        specialties = [s.strip() for s in specialties_raw.split(',') if s.strip()]
        portfolio.specialties = specialties
        
        # Custom URL (validate uniqueness)
        new_custom_url = request.POST.get('custom_url', '').strip()
        if new_custom_url and new_custom_url != portfolio.custom_url:
            if CreatorPortfolio.objects.filter(custom_url=new_custom_url).exclude(pk=portfolio.pk).exists():
                messages.error(request, 'This custom URL is already taken.')
            else:
                portfolio.custom_url = new_custom_url
                messages.success(request, 'Portfolio settings updated successfully!')
                portfolio.save()
        else:
            portfolio.save()
            messages.success(request, 'Portfolio settings updated successfully!')
        
        return redirect('dashboard:my_portfolio')
    
    context = {
        'portfolio': portfolio,
        'specialties_str': ', '.join(portfolio.specialties) if portfolio.specialties else '',
    }
    return render(request, 'dashboard/portfolio/edit_settings.html', context)


@login_required
@require_http_methods(["POST"])
def add_featured_item(request):
    """
    Add an asset or game to featured items (AJAX)
    """
    portfolio, created = CreatorPortfolio.objects.get_or_create(user=request.user)
    
    item_type = request.POST.get('item_type')
    item_id = request.POST.get('item_id')
    
    if not item_type or not item_id:
        return JsonResponse({'success': False, 'error': 'Missing parameters'}, status=400)
    
    try:
        # Check if already featured
        if item_type == 'asset':
            asset = get_object_or_404(Asset, id=item_id, creator=request.user)
            if FeaturedItem.objects.filter(portfolio=portfolio, asset=asset).exists():
                return JsonResponse({'success': False, 'error': 'Already featured'}, status=400)
            
            FeaturedItem.objects.create(
                portfolio=portfolio,
                item_type='asset',
                asset=asset
            )
        elif item_type == 'game':
            game = get_object_or_404(Game, id=item_id, creator=request.user)
            if FeaturedItem.objects.filter(portfolio=portfolio, game=game).exists():
                return JsonResponse({'success': False, 'error': 'Already featured'}, status=400)
            
            FeaturedItem.objects.create(
                portfolio=portfolio,
                item_type='game',
                game=game
            )
        else:
            return JsonResponse({'success': False, 'error': 'Invalid item type'}, status=400)
        
        return JsonResponse({'success': True, 'message': 'Item added to featured!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def remove_featured_item(request, item_id):
    """
    Remove a featured item (AJAX)
    """
    portfolio = get_object_or_404(CreatorPortfolio, user=request.user)
    featured_item = get_object_or_404(FeaturedItem, id=item_id, portfolio=portfolio)
    
    featured_item.delete()
    
    return JsonResponse({'success': True, 'message': 'Featured item removed'})


@login_required
@require_http_methods(["POST"])
def reorder_featured_items(request):
    """
    Update order of featured items (AJAX)
    """
    portfolio = get_object_or_404(CreatorPortfolio, user=request.user)
    
    # Expected format: {"items": [{"id": 1, "order": 0}, {"id": 2, "order": 1}, ...]}
    import json
    try:
        data = json.loads(request.body)
        items = data.get('items', [])
        
        for item_data in items:
            item_id = item_data.get('id')
            order = item_data.get('order')
            
            FeaturedItem.objects.filter(id=item_id, portfolio=portfolio).update(order=order)
        
        return JsonResponse({'success': True, 'message': 'Order updated'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def toggle_featured_showcase(request, item_id):
    """
    Toggle showcase status for a featured item (AJAX)
    """
    portfolio = get_object_or_404(CreatorPortfolio, user=request.user)
    featured_item = get_object_or_404(FeaturedItem, id=item_id, portfolio=portfolio)
    
    featured_item.is_showcase = not featured_item.is_showcase
    featured_item.save()
    
    return JsonResponse({
        'success': True, 
        'is_showcase': featured_item.is_showcase,
        'message': 'Showcase toggled'
    })


@login_required
def portfolio_analytics(request):
    """
    View portfolio analytics and stats
    """
    portfolio = get_object_or_404(CreatorPortfolio, user=request.user)
    
    # Date range filter
    from datetime import datetime, timedelta
    days = int(request.GET.get('days', 30))
    start_date = datetime.now().date() - timedelta(days=days)
    
    analytics = portfolio.analytics.filter(date__gte=start_date).order_by('date')
    
    # Calculate aggregates
    total_views = analytics.aggregate(Sum('views'))['views__sum'] or 0
    total_revenue = analytics.aggregate(Sum('revenue'))['revenue__sum'] or 0
    avg_time = analytics.aggregate(Avg('avg_time_on_page'))['avg_time_on_page__avg'] or 0
    
    # Chart data for frontend
    chart_data = {
        'dates': [str(a.date) for a in analytics],
        'views': [a.views for a in analytics],
        'revenue': [float(a.revenue) for a in analytics],
    }
    
    context = {
        'portfolio': portfolio,
        'analytics': analytics,
        'total_views': total_views,
        'total_revenue': total_revenue,
        'avg_time': int(avg_time),
        'chart_data': chart_data,
        'days': days,
    }
    
    return render(request, 'dashboard/portfolio/analytics.html', context)


@login_required
def manage_testimonials(request):
    """
    Manage portfolio testimonials
    """
    portfolio = get_object_or_404(CreatorPortfolio, user=request.user)
    testimonials = portfolio.testimonials.all()
    
    context = {
        'portfolio': portfolio,
        'testimonials': testimonials,
    }
    
    return render(request, 'dashboard/portfolio/testimonials.html', context)


@login_required
def add_testimonial(request):
    """
    Add a new testimonial
    """
    portfolio = get_object_or_404(CreatorPortfolio, user=request.user)
    
    if request.method == 'POST':
        author_name = request.POST.get('author_name', '')
        author_title = request.POST.get('author_title', '')
        author_avatar = request.POST.get('author_avatar', '')
        content = request.POST.get('content', '')
        rating = int(request.POST.get('rating', 5))
        
        Testimonial.objects.create(
            portfolio=portfolio,
            author_name=author_name,
            author_title=author_title,
            author_avatar=author_avatar,
            content=content,
            rating=rating,
        )
        
        messages.success(request, 'Testimonial added successfully!')
        return redirect('dashboard:manage_testimonials')
    
    return render(request, 'dashboard/portfolio/add_testimonial.html', {'portfolio': portfolio})


@login_required
@require_http_methods(["POST"])
def delete_testimonial(request, testimonial_id):
    """
    Delete a testimonial
    """
    portfolio = get_object_or_404(CreatorPortfolio, user=request.user)
    testimonial = get_object_or_404(Testimonial, id=testimonial_id, portfolio=portfolio)
    
    testimonial.delete()
    
    return JsonResponse({'success': True, 'message': 'Testimonial deleted'})
