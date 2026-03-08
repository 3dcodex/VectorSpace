"""Public games views - browsing and viewing games"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg, Q
from .models import Game, GameReview, GameComment

def game_list(request):
    """Public: Browse all published games"""
    games = Game.objects.filter(status='published').select_related('developer')
    
    # Search
    search = request.GET.get('search', '').strip()
    if search:
        games = games.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(developer__username__icontains=search)
        )
    
    # Filter by genre
    genre = request.GET.get('genre')
    if genre:
        games = games.filter(genre__icontains=genre)
    
    # Filter by platform
    platform = request.GET.get('platform')
    if platform:
        games = games.filter(platform=platform)
    
    # Sort
    sort = request.GET.get('sort', 'newest')
    if sort == 'popular':
        games = games.order_by('-downloads', '-view_count')
    elif sort == 'rating':
        games = games.order_by('-rating', '-downloads')
    else:
        games = games.order_by('-published_at', '-created_at')
    
    return render(request, 'games/list.html', {'games': games})

def game_detail(request, pk):
    """Public: View game details"""
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
def download_game(request, pk):
    """Download a game (requires login)"""
    game = get_object_or_404(Game, pk=pk)
    game.downloads += 1
    game.save()
    
    messages.success(request, f'Downloading {game.title}...')
    return redirect('games:detail', pk=pk)

@login_required
def add_review(request, pk):
    """Add or update a game review"""
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

            # Send review notification to game developer (if not self-review)
            if game.developer != request.user and created:
                from apps.core.notifications import send_notification
                rating_stars = '⭐' * int(rating)
                send_notification(
                    user=game.developer,
                    notification_type='review',
                    title=f'New review for your game: {rating_stars}',
                    message=f'{request.user.username} rated "{game.title}" {rating}/5: "{comment[:100]}..."',
                    link=f'/games/{game.id}/',
                    priority='high' if int(rating) >= 4 else 'normal',
                    related_object_id=review.id,
                    related_object_type='game_review'
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
    """Add a comment to a game"""
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
            
            # Send comment notification to game developer (if not self-comment)
            if game.developer != request.user:
                from apps.core.notifications import send_notification
                send_notification(
                    user=game.developer,
                    notification_type='comment',
                    title=f'{request.user.username} commented on your game',
                    message=f'{request.user.username} commented on "{game.title}": "{content[:100]}..."',
                    link=f'/games/{game.id}/',
                    related_object_id=comment.id,
                    related_object_type='game_comment'
                )
            
            messages.success(request, 'Comment added!')
        else:
            messages.error(request, 'Comment cannot be empty.')

    return redirect('games:detail', pk=pk)
