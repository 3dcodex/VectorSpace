"""Public competitions views - browsing competitions and leaderboards"""
from django.shortcuts import render, get_object_or_404
from django.db.models import Avg
from .models import Competition

def competition_list(request):
    """Public: Browse all competitions"""
    competitions = Competition.objects.all().order_by('-start_date')
    
    status = request.GET.get('status')
    if status:
        competitions = competitions.filter(status=status)
    
    return render(request, 'competitions/list.html', {'competitions': competitions})

def competition_detail(request, pk):
    """Public: View competition details"""
    competition = get_object_or_404(Competition, pk=pk)
    submissions = competition.submissions.all().order_by('-score')
    user_submission = None
    
    if request.user.is_authenticated:
        user_submission = submissions.filter(participant=request.user).first()
    
    return render(request, 'competitions/detail.html', {
        'competition': competition,
        'submissions': submissions,
        'user_submission': user_submission
    })

def leaderboard(request, pk):
    """Public: View competition leaderboard"""
    competition = get_object_or_404(Competition, pk=pk)
    submissions = competition.submissions.annotate(
        avg_score=Avg('votes__score')
    ).order_by('-avg_score', '-score')
    
    return render(request, 'competitions/public_leaderboard.html', {
        'competition': competition,
        'submissions': submissions
    })
