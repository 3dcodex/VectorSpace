from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Avg, Count
from .models import Game, GameVersion, GameReview
from django.utils import timezone

@login_required
def my_games(request):
    """Developer dashboard - manage your games"""
    games = Game.objects.filter(developer=request.user).order_by('-created_at')
    
    total_games = games.count()
    published_games = games.filter(status='published').count()
    in_development = games.filter(status='draft').count()
    total_downloads = games.aggregate(total=Sum('downloads'))['total'] or 0
    avg_rating = games.aggregate(avg=Avg('rating'))['avg'] or 0
    total_reviews = GameReview.objects.filter(game__developer=request.user).count()
    
    context = {
        'games': games,
        'total_games': total_games,
        'published_games': published_games,
        'in_development': in_development,
        'total_downloads': total_downloads,
        'avg_rating': avg_rating,
        'total_reviews': total_reviews,
    }
    
    return render(request, 'games/my_games.html', context)
