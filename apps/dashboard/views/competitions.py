from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from apps.competitions.models import Competition, Submission, Vote
from apps.competitions.forms import CompetitionForm, SubmissionForm, VoteForm

@login_required
def my_competitions(request):
    """List competitions created by user"""
    competitions = Competition.objects.filter(organizer=request.user).order_by('-start_date')
    return render(request, 'dashboard/competitions/my_competitions.html', {'competitions': competitions})

@login_required
def create_competition(request):
    """Create a new competition"""
    # Vector-only users can participate but cannot create competitions.
    if not (request.user.is_staff or request.user.profile.has_professional_role()):
        messages.error(request, 'Professional role required to create competitions.')
        return redirect('dashboard:overview')

    if request.method == 'POST':
        form = CompetitionForm(request.POST)
        if form.is_valid():
            competition = form.save(commit=False)
            competition.organizer = request.user
            competition.save()
            messages.success(request, 'Competition created!')
            return redirect('dashboard:dashboard_competitions_my_competitions')
    else:
        form = CompetitionForm()
    
    return render(request, 'dashboard/competitions/create.html', {'form': form})

@login_required
def my_submissions(request):
    """List user's competition submissions"""
    submissions = Submission.objects.filter(participant=request.user).order_by('-submitted_at')
    return render(request, 'dashboard/competitions/my_submissions.html', {'submissions': submissions})

@login_required
def submit_entry(request, pk):
    """Submit entry to a competition"""
    competition = get_object_or_404(Competition, pk=pk)
    
    # Check if already submitted
    if Submission.objects.filter(competition=competition, participant=request.user).exists():
        messages.info(request, 'You have already submitted to this competition.')
        return redirect('dashboard:dashboard_competitions_my_submissions')
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.competition = competition
            submission.participant = request.user
            submission.save()
            messages.success(request, 'Submission successful!')
            return redirect('dashboard:dashboard_competitions_my_submissions')
    else:
        form = SubmissionForm()
    
    return render(request, 'dashboard/competitions/submit.html', {
        'form': form,
        'competition': competition
    })

@login_required
def vote_submission(request, pk):
    """Vote on a competition submission"""
    submission = get_object_or_404(Submission, pk=pk)
    
    if request.method == 'POST':
        form = VoteForm(request.POST)
        if form.is_valid():
            vote, created = Vote.objects.update_or_create(
                submission=submission,
                voter=request.user,
                defaults={'score': form.cleaned_data['score']}
            )
            
            # Update submission score
            avg_score = submission.votes.aggregate(Avg('score'))['score__avg']
            submission.score = avg_score or 0
            submission.save()
            
            messages.success(request, 'Vote recorded!')
    
    return redirect('competitions:detail', pk=submission.competition.pk)


