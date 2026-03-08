from django.shortcuts import render
from django.db.models import Avg, Count
from django.db.models.functions import Coalesce
from apps.users.models import User
from apps.marketplace.models import Asset
from apps.games.models import Game
from apps.jobs.models import Job

def home(request):
    context = {
        'total_users': User.objects.count(),
        'total_assets': Asset.objects.count(),
        'total_games': Game.objects.filter(status='published').count(),
        'total_jobs': Job.objects.filter(active=True).count(),
        'featured_assets': Asset.objects.filter(is_active=True).order_by('-created_at')[:6],
        'featured_games': Game.objects.filter(status='published').order_by('-created_at')[:6],
        'top_rated_assets': Asset.objects.filter(is_active=True).annotate(
            avg_rating=Coalesce(Avg('reviews__rating'), 0.0),
            review_count=Count('reviews')
        ).filter(review_count__gt=0).order_by('-avg_rating', '-downloads')[:6],
    }
    return render(request, 'home.html', context)

def custom_403(request, exception=None):
    return render(request, '403.html', status=403)

def custom_404(request, exception=None):
    return render(request, '404.html', status=404)

def custom_500(request):
    return render(request, '500.html', status=500)
