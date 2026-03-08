"""
Advanced Search & Discovery Views
Full-text search, trending, similar items, etc.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count, Avg, Value, CharField
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta

from apps.marketplace.models import Asset
from apps.games.models import Game
from apps.marketplace.search_models import (
    SearchQuery, SavedSearch, TrendingItem, SimilarItem, 
    SearchAnalytics
)


# Public search views

def advanced_search(request):
    """
    Advanced search page with filters
    """
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'assets')  # assets, games, all
    
    # Get filters from request
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    min_rating = request.GET.get('min_rating', '')
    tags = request.GET.get('tags', '').split(',') if request.GET.get('tags') else []
    tags = [t.strip() for t in tags if t.strip()]
    
    sort_by = request.GET.get('sort', 'relevance')
    
    # Build base querysets
    assets = Asset.objects.filter(is_active=True)
    games = Game.objects.filter(status='published')
    
    results = []
    filters_applied = {}
    
    # Apply search query
    if query:
        # Full-text search
        assets = assets.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query)
        )
        # Games don't have tags field, only search title and description
        games = games.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)
        )
        filters_applied['query'] = query
    
    # Apply category filter
    if category:
        if search_type in ['assets', 'all']:
            assets = assets.filter(category=category)
        if search_type in ['games', 'all']:
            # Games use 'genre' field instead of 'category'
            games = games.filter(genre=category)
        filters_applied['category'] = category
    
    # Apply price filter (Assets only - Games don't have price field)
    if min_price:
        try:
            min_price = float(min_price)
            if search_type in ['assets', 'all']:
                assets = assets.filter(price__gte=min_price)
            filters_applied['min_price'] = min_price
        except ValueError:
            pass
    
    if max_price:
        try:
            max_price = float(max_price)
            if search_type in ['assets', 'all']:
                assets = assets.filter(price__lte=max_price)
            filters_applied['max_price'] = max_price
        except ValueError:
            pass
    
    # Apply rating filter
    if min_rating:
        try:
            min_rating = float(min_rating)
            if search_type in ['assets', 'all']:
                assets = assets.filter(rating__gte=min_rating)
            if search_type in ['games', 'all']:
                games = games.filter(rating__gte=min_rating)
            filters_applied['min_rating'] = min_rating
        except ValueError:
            pass
    
    # Apply tag filter (Assets only - Games don't have tags)
    if tags:
        if search_type in ['assets', 'all']:
            for tag in tags:
                assets = assets.filter(tags__icontains=tag)
        filters_applied['tags'] = tags
    
    # Apply sorting
    if search_type in ['assets', 'all']:
        if sort_by == 'newest':
            assets = assets.order_by('-created_at')
        elif sort_by == 'price_low':
            assets = assets.order_by('price')
        elif sort_by == 'price_high':
            assets = assets.order_by('-price')
        elif sort_by == 'rating':
            assets = assets.order_by('-rating')
        elif sort_by == 'popular':
            assets = assets.annotate(popularity=Count('wishlists')).order_by('-popularity')
        else:  # relevance - title match is better
            assets = assets.annotate(
                title_match=Case(
                    When(title__icontains=query, then=Value(1)),
                    default=Value(0),
                    output_field=CharField()
                )
            ).order_by('-title_match', '-rating')
    
    if search_type in ['games', 'all']:
        if sort_by == 'newest':
            games = games.order_by('-created_at')
        elif sort_by == 'rating':
            games = games.order_by('-rating')
        else:  # relevance and price sorts aren't applicable for games
            games = games.order_by('-rating')
    
    # Combine results
    if search_type == 'assets':
        results = list(assets)
    elif search_type == 'games':
        results = list(games)
    else:  # all
        results = list(assets) + list(games)
    
    # Record search query
    if query and request.user.is_authenticated:
        SearchQuery.objects.create(
            user=request.user,
            query_text=query,
            search_type=search_type,
            results_count=len(results),
            filters_applied=filters_applied,
        )
    
    # Get available filters for sidebar
    categories = Asset.objects.filter(is_active=True).values_list('category', flat=True).distinct()
    if search_type == 'games':
        categories = Game.objects.filter(status='published').values_list('genre', flat=True).distinct()
    
    # Get price ranges (Assets only - Games don't have price)
    asset_prices = Asset.objects.filter(is_active=True).aggregate(min=Min('price'), max=Max('price'))
    
    # Pagination
    paginator = Paginator(results, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'query': query,
        'search_type': search_type,
        'page_obj': page_obj,
        'sort_by': sort_by,
        'category': category,
        'min_price': min_price,
        'max_price': max_price,
        'min_rating': min_rating,
        'tags': ','.join(tags),
        'categories': categories,
        'asset_price_min': asset_prices.get('min', 0),
        'asset_price_max': asset_prices.get('max', 1000),
        'results_count': len(results),
    }
    
    return render(request, 'marketplace/search.html', context)


def trending_items(request):
    """
    View trending assets and games
    """
    period = request.GET.get('period', 'month')  # today, week, month, all_time
    item_type = request.GET.get('type', 'all')  # asset, game, all
    
    trending = TrendingItem.objects.filter(period=period)
    
    if item_type == 'asset':
        trending = trending.filter(item_type='asset')
    elif item_type == 'game':
        trending = trending.filter(item_type='game')
    
    trending = trending.select_related('asset', 'game').order_by('ranking')[:50]
    
    context = {
        'trending': trending,
        'period': period,
        'item_type': item_type,
    }
    
    return render(request, 'marketplace/trending.html', context)


def similar_to_asset(request, asset_id):
    """
    Get items similar to a specific asset
    """
    asset = get_object_or_404(Asset, id=asset_id, is_active=True)
    
    # Get pre-calculated similar items
    similar = SimilarItem.objects.filter(source_asset=asset).select_related(
        'similar_asset', 'similar_game'
    ).order_by('-similarity_score')[:12]
    
    context = {
        'asset': asset,
        'similar_items': similar,
    }
    
    return render(request, 'marketplace/similar.html', context)


@require_http_methods(["GET"])
def search_suggestions(request):
    """
    AJAX endpoint for search suggestions
    """
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'assets')
    
    if not query or len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    suggestions = []
    
    # Asset suggestions
    if search_type in ['assets', 'all']:
        assets = Asset.objects.filter(
            is_active=True,
            title__icontains=query
        ).values_list('title', flat=True).distinct()[:5]
        suggestions.extend([{'type': 'asset', 'text': title} for title in assets])
    
    # Game suggestions
    if search_type in ['games', 'all']:
        games = Game.objects.filter(
            status='published',
            title__icontains=query
        ).values_list('title', flat=True).distinct()[:5]
        suggestions.extend([{'type': 'game', 'text': title} for title in games])
    
    # Tag suggestions
    if search_type == 'all':
        assets = Asset.objects.filter(is_active=True, tags__icontains=query)
        # Extract tags containing query
        tags_set = set()
        for asset in assets[:20]:
            if asset.tags:
                for tag in asset.tags.split(','):
                    tag = tag.strip()
                    if query.lower() in tag.lower():
                        tags_set.add(tag)
        
        suggestions.extend([{'type': 'tag', 'text': tag} for tag in list(tags_set)[:5]])
    
    return JsonResponse({'suggestions': suggestions})


# Dashboard search management

@login_required
def my_searches(request):
    """
    View user's search history and saved searches
    """
    # Get saved searches
    saved_searches = SavedSearch.objects.filter(user=request.user)
    
    # Get recent search history
    recent_searches = SearchQuery.objects.filter(user=request.user)[:50]
    
    context = {
        'saved_searches': saved_searches,
        'recent_searches': recent_searches,
    }
    
    return render(request, 'dashboard/search_history.html', context)


@login_required
def save_search(request):
    """
    Save current search for quick re-run
    """
    if request.method == 'POST':
        name = request.POST.get('name', '')
        search_type = request.POST.get('search_type', 'assets')
        query_text = request.POST.get('query', '')
        
        # Collect all filters
        filters = {
            'category': request.POST.get('category', ''),
            'min_price': request.POST.get('min_price', ''),
            'max_price': request.POST.get('max_price', ''),
            'min_rating': request.POST.get('min_rating', ''),
            'tags': request.POST.get('tags', ''),
            'sort_by': request.POST.get('sort', 'relevance'),
        }
        
        saved_search, created = SavedSearch.objects.update_or_create(
            user=request.user,
            name=name,
            defaults={
                'search_type': search_type,
                'query_text': query_text,
                'filters': filters,
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': f"Search '{name}' saved!" if created else f"Search '{name}' updated!",
            'search_id': saved_search.id,
        })
    
    return JsonResponse({'success': False, 'error': 'POST required'}, status=400)


@login_required
@require_http_methods(["POST"])
def delete_saved_search(request, search_id):
    """
    Delete a saved search
    """
    saved_search = get_object_or_404(SavedSearch, id=search_id, user=request.user)
    name = saved_search.name
    saved_search.delete()
    
    return JsonResponse({
        'success': True,
        'message': f"Search '{name}' deleted"
    })


@login_required
def run_saved_search(request, search_id):
    """
    Re-run a saved search
    """
    saved_search = get_object_or_404(SavedSearch, id=search_id, user=request.user)
    
    # Update last run
    saved_search.last_run = timezone.now()
    saved_search.run_count += 1
    saved_search.save()
    
    # Build redirect URL with search parameters
    params = [f"q={saved_search.query_text}"]
    params.append(f"type={saved_search.search_type}")
    
    if saved_search.filters:
        filters = saved_search.filters
        if filters.get('category'):
            params.append(f"category={filters['category']}")
        if filters.get('min_price'):
            params.append(f"min_price={filters['min_price']}")
        if filters.get('max_price'):
            params.append(f"max_price={filters['max_price']}")
        if filters.get('min_rating'):
            params.append(f"min_rating={filters['min_rating']}")
        if filters.get('tags'):
            params.append(f"tags={filters['tags']}")
        if filters.get('sort_by'):
            params.append(f"sort={filters['sort_by']}")
    
    return redirect(f"/marketplace/search/?{'&'.join(params)}")


# Admin/Analytics views

def search_analytics(request):
    """
    Search analytics dashboard (admin only)
    """
    if not request.user.is_staff:
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied
    
    # Last 30 days
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    analytics = SearchAnalytics.objects.filter(date__gte=thirty_days_ago).order_by('-date')
    
    # Aggregate stats
    total_searches = SearchQuery.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).count()
    
    # Top searches
    top_searches = SearchQuery.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30)
    ).values('query_text').annotate(count=Count('id')).order_by('-count')[:20]
    
    # Click through rate
    clicked_searches = SearchQuery.objects.filter(
        created_at__gte=timezone.now() - timedelta(days=30),
        clicked_result=True
    ).count()
    ctr = (clicked_searches / total_searches * 100) if total_searches > 0 else 0
    
    context = {
        'analytics': analytics,
        'total_searches': total_searches,
        'top_searches': top_searches,
        'click_through_rate': ctr,
    }
    
    return render(request, 'admin/search_analytics.html', context)


# Utility functions for calculations

def calculate_trending_items():
    """
    Calculate trending items based on recent activity
    Should be run periodically via celery task or management command
    """
    
    seven_days_ago = timezone.now() - timedelta(days=7)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Calculate for each period
    for period, days_back in [('today', 1), ('week', 7), ('month', 30), ('all_time', 999999)]:
        cutoff_date = timezone.now() - timedelta(days=days_back)
        
        # Assets
        asset_scores = Asset.objects.filter(
            is_active=True,
            created_at__gte=cutoff_date
        ).annotate(
            recent_views=Count('id'),  # Would need a view tracking table
            recent_purchases=Count('id'),  # Placeholder
            avg_rating=Avg('rating'),
        )
        
        for idx, asset in enumerate(asset_scores[:50]):
            # Simple scoring: views (0.4) + purchases*10 (0.4) + rating (0.2)
            score = (
                (asset.recent_views or 0) * 0.4 +
                (asset.recent_purchases or 0) * 10 * 0.4 +
                (asset.avg_rating or 0) * 2 * 0.2
            )
            
            TrendingItem.objects.update_or_create(
                item_type='asset',
                asset=asset,
                period=period,
                defaults={
                    'score': score,
                    'ranking': idx + 1,
                    'views_30d': asset.recent_views or 0,
                    'purchases_30d': asset.recent_purchases or 0,
                    'rating_avg': asset.avg_rating or 0,
                }
            )


def calculate_similar_items():
    """
    Calculate similar items based on category, tags, etc.
    """
    for asset in Asset.objects.filter(is_active=True):
        # Find similar assets
        similar_assets = Asset.objects.filter(
            is_active=True,
            category=asset.category
        ).exclude(id=asset.id)[:20]
        
        for similar in similar_assets:
            # Calculate similarity score
            matching_tags = 0
            if asset.tags and similar.tags:
                asset_tags = set(asset.tags.split(','))
                similar_tags = set(similar.tags.split(','))
                matching_tags = len(asset_tags & similar_tags)
            
            matching_category = asset.category == similar.category
            
            # Score: tags (0-0.4) + category (0.6)
            score = min(matching_tags / 3, 1) * 0.4 + (0.6 if matching_category else 0)
            
            if score > 0.1:  # Only save if meaningful
                SimilarItem.objects.update_or_create(
                    source_asset=asset,
                    similar_asset=similar,
                    defaults={
                        'similarity_score': score,
                        'matching_tags': matching_tags,
                        'matching_category': matching_category,
                    }
                )


from django.db.models import Min, Max, Case, When
