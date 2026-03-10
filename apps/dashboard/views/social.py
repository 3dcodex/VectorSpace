from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages as django_messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from apps.social.models import Post, Follow, Message, PostVote, PostLike, Category
from apps.social.forms import PostForm, CommentForm, MessageForm
from apps.users.models import User

@login_required
def feed(request):
    """Personal feed with posts from followed users"""
    posts = Post.objects.select_related('author').order_by('-created_at')[:20]
    
    user_posts_count = Post.objects.filter(author=request.user).count()
    user_followers_count = Follow.objects.filter(following=request.user).count()
    
    trending = []
    top_contributors = []
    
    context = {
        'posts': posts,
        'user_posts_count': user_posts_count,
        'user_followers_count': user_followers_count,
        'trending': trending,
        'top_contributors': top_contributors,
    }
    return render(request, 'social/feed.html', context)

@login_required
def my_posts(request):
    """List user's posts"""
    posts = Post.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'social/my_posts.html', {'posts': posts})

@login_required
def create_post(request):
    """Create a new post"""
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            django_messages.success(request, 'Post created!')
            return redirect('social:community')
    else:
        form = PostForm()
    
    categories = Category.objects.all()
    return render(request, 'social/create_post.html', {'form': form, 'categories': categories})

@login_required
def like_post(request, pk):
    """Like/unlike a post"""
    post = get_object_or_404(Post, pk=pk)
    like, created = PostLike.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        post.likes_count = max(0, post.likes_count - 1)
    else:
        post.likes_count += 1

    post.save()
    return redirect(request.META.get('HTTP_REFERER', 'social_feed'))

@login_required
def vote_post(request, pk, vote_type):
    """Upvote/downvote a post"""
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
    return redirect(request.META.get('HTTP_REFERER', 'social_feed'))

@login_required
def add_comment(request, pk):
    """Add comment to a post"""
    post = get_object_or_404(Post, pk=pk)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            
            # Send comment notification to post author (if not self-comment)
            if post.author != request.user:
                from apps.core.notifications import send_notification
                send_notification(
                    user=post.author,
                    notification_type='comment',
                    title=f'{request.user.username} commented on your post',
                    message=f'{request.user.username} commented: "{comment.content[:100]}..."',
                    link=f'/community/post/{post.id}/',
                    related_object_id=comment.id,
                    related_object_type='comment'
                )
    return redirect('social:post_detail', pk=pk)

@login_required
def messages_list(request):
    """List all conversations"""
    sent = Message.objects.filter(sender=request.user).values_list('recipient_id', flat=True)
    received = Message.objects.filter(recipient=request.user).values_list('sender_id', flat=True)
    user_ids = set(list(sent) + list(received))
    users = User.objects.filter(id__in=user_ids)
    
    return render(request, 'social/messages_list.html', {'users': users})

@login_required
def conversation(request, user_id):
    """View conversation with a specific user"""
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
            return redirect('social_conversation', user_id=user_id)
    else:
        form = MessageForm()
    
    return render(request, 'social/conversation.html', {
        'other_user': other_user,
        'messages': messages,
        'form': form
    })

@login_required
def follow_user(request, user_id):
    """Follow/unfollow a user"""
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
        # Send follow notification
        from apps.core.notifications import send_notification
        send_notification(
            user=user_to_follow,
            notification_type='follow',
            title=f'{request.user.username} started following you',
            message=f'{request.user.username} is now following your profile and will see your posts.',
            link=f'/community/profile/{request.user.id}/',
            related_object_id=request.user.id,
            related_object_type='user'
        )
        django_messages.success(request, f'Now following {user_to_follow.username}')
    
    return redirect('dashboard:social_profile', user_id=user_id)

@login_required
def user_profile(request, user_id):
    """View user profile (dashboard version)"""
    profile_user = get_object_or_404(User, pk=user_id)
    posts = Post.objects.filter(author=profile_user).order_by('-created_at')
    is_following = False
    
    if request.user.is_authenticated and request.user != profile_user:
        is_following = Follow.objects.filter(follower=request.user, following=profile_user).exists()
    
    return render(request, 'dashboard/profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'is_following': is_following
    })

@login_required
def my_profile(request):
    """View own dashboard profile"""
    return user_profile(request, request.user.pk)

@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        user = request.user
        user.bio = request.POST.get('bio', '')
        user.portfolio_url = request.POST.get('portfolio_url', '')
        
        # Handle skills
        skills_str = request.POST.get('skills', '')
        user.skills = [s.strip() for s in skills_str.split(',') if s.strip()]
        
        # Handle full name
        full_name = request.POST.get('full_name', '')
        if full_name:
            name_parts = full_name.split(' ', 1)
            user.first_name = name_parts[0]
            user.last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        user.save()
        
        # Update profile
        profile = user.profile
        requested_user_type = request.POST.get('user_type', '').strip().lower()
        role_map = {
            'artist': 'CREATOR',
            'vfx': 'CREATOR',
            'developer': 'DEVELOPER',
            'recruiter': 'RECRUITER',
            'mentor': 'MENTOR',
            'gamer': 'VECTOR',
            'player': 'VECTOR',
            'vector': 'VECTOR',
        }
        if requested_user_type in role_map:
            profile.primary_role = role_map[requested_user_type]
        profile.location = request.POST.get('location', '')
        profile.experience_years = int(request.POST.get('experience_years', 0))
        profile.github = request.POST.get('github', '')
        profile.linkedin = request.POST.get('linkedin', '')
        profile.artstation = request.POST.get('artstation', '')
        profile.youtube = request.POST.get('youtube', '')
        
        # Handle resume upload
        if request.FILES.get('resume'):
            profile.resume = request.FILES['resume']
        
        # Handle avatar upload
        if request.FILES.get('avatar'):
            user.avatar = request.FILES['avatar']
            user.save()
        
        profile.save()
        
        django_messages.success(request, 'Profile updated successfully!')
        return redirect('dashboard:social_profile', user_id=user.id)
    
    return render(request, 'dashboard/edit_profile.html')

@login_required
def settings(request):
    """User settings page"""
    from apps.users.models import UserSettings
    settings_obj, _ = UserSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_email':
            new_email = request.POST.get('email')
            if new_email:
                request.user.email = new_email
                request.user.save()
                return JsonResponse({'success': True, 'message': 'Email updated'})
        
        elif action == 'update_password':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            if request.user.check_password(old_password):
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                return JsonResponse({'success': True, 'message': 'Password updated'})
            return JsonResponse({'success': False, 'message': 'Incorrect password'})
        
        elif action == 'toggle_setting':
            field = request.POST.get('field')
            value = request.POST.get('value') == 'true'
            if hasattr(settings_obj, field):
                setattr(settings_obj, field, value)
                settings_obj.save()
                return JsonResponse({'success': True})
        
        elif action == 'switch_role':
            # Admin-only feature to preview different role dashboards
            if request.user.is_staff or request.user.is_superuser:
                new_role = request.POST.get('role')
                valid_roles = ['VECTOR', 'CREATOR', 'DEVELOPER', 'RECRUITER', 'MENTOR']
                if new_role == 'MODERATOR':
                    request.user.profile.admin_view_as_role = None
                    request.user.profile.save(update_fields=['admin_view_as_role'])
                    return JsonResponse({
                        'success': True,
                        'message': 'Switched to moderator mode',
                        'role': 'MODERATOR'
                    })
                if new_role in valid_roles:
                    request.user.profile.admin_view_as_role = new_role
                    request.user.profile.save(update_fields=['admin_view_as_role'])
                    return JsonResponse({
                        'success': True, 
                        'message': f'Now viewing as {new_role}',
                        'role': new_role
                    })
                return JsonResponse({'success': False, 'message': 'Invalid role'})
            return JsonResponse({'success': False, 'message': 'Admin access required'})

        elif action == 'upgrade_role':
            requested_role = request.POST.get('role')
            valid_roles = ['CREATOR', 'DEVELOPER', 'RECRUITER', 'MENTOR']
            if requested_role not in valid_roles:
                return JsonResponse({'success': False, 'message': 'Invalid role request'})

            profile = request.user.profile
            secondary_roles = profile.secondary_roles or []
            if requested_role == profile.primary_role or requested_role in secondary_roles:
                return JsonResponse({'success': True, 'message': f'You already have {requested_role} access'})

            secondary_roles.append(requested_role)
            profile.secondary_roles = secondary_roles
            profile.save(update_fields=['secondary_roles'])
            return JsonResponse({'success': True, 'message': f'{requested_role} tools unlocked'})
        
        elif action == 'deactivate':
            request.user.is_active = False
            request.user.save()
            return JsonResponse({'success': True, 'redirect': '/'})
        
        elif action == 'delete':
            request.user.delete()
            return JsonResponse({'success': True, 'redirect': '/'})
    
    return render(request, 'dashboard/settings.html', {'settings': settings_obj})
