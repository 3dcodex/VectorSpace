from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.games.models import Game
from apps.games.forms import GamePublishForm

@login_required
def my_games(request):
    """List user's published games"""
    games = Game.objects.filter(developer=request.user).order_by('-created_at')
    return render(request, 'games/my_games.html', {'games': games})

@login_required
def publish_game(request):
    """Publish a new game"""
    if request.method == 'POST':
        form = GamePublishForm(request.POST, request.FILES)
        if form.is_valid():
            game = form.save(commit=False)
            game.developer = request.user
            game.status = 'published'
            game.published_at = timezone.now()
            game.save()
            
            messages.success(request, f'Game "{game.title}" published successfully!')
            return redirect('games:detail', pk=game.pk)
    else:
        form = GamePublishForm()
    
    return render(request, 'games/publish.html', {'form': form})

@login_required
def edit_game(request, pk):
    """Edit a published game"""
    game = get_object_or_404(Game, pk=pk, developer=request.user)
    
    if request.method == 'POST':
        form = GamePublishForm(request.POST, request.FILES, instance=game)
        if form.is_valid():
            form.save()
            messages.success(request, f'Game "{game.title}" updated successfully!')
            return redirect('games_my_games')
    else:
        form = GamePublishForm(instance=game)
    
    return render(request, 'games/publish.html', {'form': form, 'game': game})


