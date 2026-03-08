from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from apps.marketplace.models import Asset
from apps.games.models import Game
from apps.social.models import Post
from apps.jobs.models import Application
from apps.competitions.models import Submission

@login_required
def dashboard_overview(request):
    user = request.user
    
    context = {
        'assets_count': Asset.objects.filter(seller=user).count(),
        'games_count': Game.objects.filter(developer=user).count(),
        'posts_count': Post.objects.filter(author=user).count(),
        'applications_count': Application.objects.filter(applicant=user).count(),
        'entries_count': Submission.objects.filter(participant=user).count(),
        'recent_assets': Asset.objects.filter(seller=user).order_by('-created_at')[:3],
        'recent_games': Game.objects.filter(developer=user).order_by('-created_at')[:3],
        'recent_posts': Post.objects.filter(author=user).order_by('-created_at')[:5],
        'total_sales': Asset.objects.filter(seller=user).aggregate(total=Sum('downloads'))['total'] or 0,
    }
    
    return render(request, 'dashboard/overview.html', context)
