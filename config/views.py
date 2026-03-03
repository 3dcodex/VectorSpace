from django.shortcuts import render
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
        'featured_assets': Asset.objects.order_by('-created_at')[:6],
        'featured_games': Game.objects.filter(status='published').order_by('-created_at')[:6],
    }
    return render(request, 'home.html', context)
