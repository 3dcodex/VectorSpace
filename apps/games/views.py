from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg
from .models import Game, GameVersion, GameReview, GameComment
from .forms import GamePublishForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Game, GameVersion
from .forms import GamePublishForm

def game_list(request):
    games = Game.objects.filter(status='published').order_by('-published_at')
    
    genre = request.GET.get('genre')
    search = request.GET.get('search')
    
    if genre:
        games = games.filter(genre__icontains=genre)
    if search:
        games = games.filter(title__icontains=search)
    
    return render(request, 'games/list.html', {'games': games})

def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)
    versions = game.versions.all().order_by('-created_at')
    reviews = game.reviews.all().select_related('user').order_by('-created_at')
    comments = game.comments.filter(parent=None).select_related('user').order_by('-created_at')

    # Calculate average rating
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    game.rating = round(avg_rating, 1)
    game.save()

    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    return render(request, 'games/detail.html', {
        'game': game,
        'versions': versions,
        'reviews': reviews,
        'comments': comments,
        'user_review': user_review,
        'avg_rating': avg_rating,
    })

@login_required
def publish_game(request):
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
def download_game(request, pk):
    game = get_object_or_404(Game, pk=pk)
    game.downloads += 1
    game.save()
    
    messages.success(request, f'Downloading {game.title}...')
    return redirect('games:detail', pk=pk)

@login_required
def my_games(request):
    games = Game.objects.filter(developer=request.user).order_by('-created_at')
    return render(request, 'games/my_games.html', {'games': games})
@login_required
def add_review(request, pk):
    game = get_object_or_404(Game, pk=pk)

    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        if rating and comment:
            review, created = GameReview.objects.update_or_create(
                game=game,
                user=request.user,
                defaults={'rating': int(rating), 'comment': comment}
            )

            if created:
                messages.success(request, 'Review added successfully!')
            else:
                messages.success(request, 'Review updated successfully!')
        else:
            messages.error(request, 'Please provide both rating and comment.')

    return redirect('games:detail', pk=pk)

@login_required
def add_comment(request, pk):
    game = get_object_or_404(Game, pk=pk)

    if request.method == 'POST':
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')

        if content:
            comment = GameComment.objects.create(
                game=game,
                user=request.user,
                content=content,
                parent_id=parent_id if parent_id else None
            )
            messages.success(request, 'Comment added!')
        else:
            messages.error(request, 'Comment cannot be empty.')

    return redirect('games:detail', pk=pk)
