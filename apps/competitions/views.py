from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Avg
from .models import Competition, Submission, Vote
from .forms import CompetitionForm, SubmissionForm, VoteForm

def competition_list(request):
    competitions = Competition.objects.all().order_by('-start_date')
    
    status = request.GET.get('status')
    if status:
        competitions = competitions.filter(status=status)
    
    return render(request, 'competitions/list.html', {'competitions': competitions})

def competition_detail(request, pk):
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

@login_required
def create_competition(request):
    if request.method == 'POST':
        form = CompetitionForm(request.POST)
        if form.is_valid():
            competition = form.save(commit=False)
            competition.organizer = request.user
            competition.save()
            messages.success(request, 'Competition created!')
            return redirect('competitions:detail', pk=competition.pk)
    else:
        form = CompetitionForm()
    
    return render(request, 'competitions/create.html', {'form': form})

@login_required
def submit_entry(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    
    # Check if already submitted
    if Submission.objects.filter(competition=competition, participant=request.user).exists():
        messages.info(request, 'You have already submitted to this competition.')
        return redirect('competitions:detail', pk=pk)
    
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.competition = competition
            submission.participant = request.user
            submission.save()
            messages.success(request, 'Submission successful!')
            return redirect('competitions:detail', pk=pk)
    else:
        form = SubmissionForm()
    
    return render(request, 'competitions/submit.html', {
        'form': form,
        'competition': competition
    })

def leaderboard(request, pk):
    competition = get_object_or_404(Competition, pk=pk)
    submissions = competition.submissions.annotate(
        avg_score=Avg('votes__score')
    ).order_by('-avg_score', '-score')
    
    return render(request, 'competitions/leaderboard.html', {
        'competition': competition,
        'submissions': submissions
    })

@login_required
def vote_submission(request, pk):
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
