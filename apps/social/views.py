from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.db.models import Q
from .models import Post, Comment, Follow, Message, PostVote, PostLike
from .forms import PostForm, CommentForm, MessageForm
from apps.users.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.db.models import Q
from .models import Post, Comment, Follow, Message
from .forms import PostForm, CommentForm, MessageForm
from apps.users.models import User

@login_required
def feed(request):
    # Get posts from followed users and own posts
    following_ids = Follow.objects.filter(follower=request.user).values_list('following_id', flat=True)
    posts = Post.objects.filter(
        Q(author__in=following_ids) | Q(author=request.user)
    ).order_by('-created_at').select_related('author')
    
    return render(request, 'social/feed.html', {'posts': posts})

@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            django_messages.success(request, 'Post created!')
            return redirect('social:feed')
    else:
        form = PostForm()
    
    return render(request, 'social/create_post.html', {'form': form})

@login_required
def like_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = PostLike.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        post.likes_count = max(0, post.likes_count - 1)
    else:
        post.likes_count += 1

    post.save()
    return redirect(request.META.get('HTTP_REFERER', 'social:feed'))
@login_required
def vote_post(request, pk, vote_type):
    post = get_object_or_404(Post, pk=pk)

    # Remove existing vote if any
    existing_vote = PostVote.objects.filter(user=request.user, post=post).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # Remove vote if clicking same button
            if vote_type == 'upvote':
                post.upvotes = max(0, post.upvotes - 1)
            else:
                post.downvotes = max(0, post.downvotes - 1)
            existing_vote.delete()
        else:
            # Switch vote
            if vote_type == 'upvote':
                post.upvotes += 1
                post.downvotes = max(0, post.downvotes - 1)
            else:
                post.downvotes += 1
                post.upvotes = max(0, post.upvotes - 1)
            existing_vote.vote_type = vote_type
            existing_vote.save()
    else:
        # New vote
        PostVote.objects.create(user=request.user, post=post, vote_type=vote_type)
        if vote_type == 'upvote':
            post.upvotes += 1
        else:
            post.downvotes += 1

    post.save()
    return redirect(request.META.get('HTTP_REFERER', 'social:feed'))

@login_required
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
    return redirect('social:feed')

@login_required
def messages_list(request):
    # Get unique conversations
    sent = Message.objects.filter(sender=request.user).values_list('recipient_id', flat=True)
    received = Message.objects.filter(recipient=request.user).values_list('sender_id', flat=True)
    user_ids = set(list(sent) + list(received))
    users = User.objects.filter(id__in=user_ids)
    
    return render(request, 'social/messages_list.html', {'users': users})

@login_required
def conversation(request, user_id):
    other_user = get_object_or_404(User, pk=user_id)
    messages = Message.objects.filter(
        Q(sender=request.user, recipient=other_user) |
        Q(sender=other_user, recipient=request.user)
    ).order_by('created_at')
    
    # Mark as read
    Message.objects.filter(sender=other_user, recipient=request.user, read=False).update(read=True)
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            message.recipient = other_user
            message.save()
            return redirect('social:conversation', user_id=user_id)
    else:
        form = MessageForm()
    
    return render(request, 'social/conversation.html', {
        'other_user': other_user,
        'messages': messages,
        'form': form
    })

@login_required
def user_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    posts = Post.objects.filter(author=user).order_by('-created_at')
    is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    
    return render(request, 'social/profile.html', {
        'profile_user': user,
        'posts': posts,
        'is_following': is_following
    })

@login_required
def follow_user(request, user_id):
    user_to_follow = get_object_or_404(User, pk=user_id)
    
    if user_to_follow == request.user:
        django_messages.error(request, "You cannot follow yourself.")
        return redirect('social:profile', user_id=user_id)
    
    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )
    
    if not created:
        follow.delete()
        django_messages.info(request, f'Unfollowed {user_to_follow.username}')
    else:
        django_messages.success(request, f'Now following {user_to_follow.username}')
    
    return redirect('social:profile', user_id=user_id)
