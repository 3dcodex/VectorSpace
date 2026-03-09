"""Public social views - browsing community posts and profiles"""
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Post, Category
from apps.social.models import PostVote
from .forms import CommentForm
from apps.users.models import User

def community(request):
    """Public: Browse community posts"""
    category_slug = request.GET.get('category')
    search_query = request.GET.get('search', '')
    
    posts = Post.objects.select_related('author', 'category').annotate(
        comment_count=Count('comments')
    ).order_by('-created_at')
    
    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    
    if search_query:
        posts = posts.filter(Q(title__icontains=search_query) | Q(content__icontains=search_query))
    
    paginator = Paginator(posts, 10)
    page = request.GET.get('page', 1)
    posts_page = paginator.get_page(page)
    
    categories = Category.objects.all()
    top_contributors = User.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:5]
    
    context = {
        'posts': posts_page,
        'categories': categories,
        'top_contributors': top_contributors,
        'active_category': category_slug,
        'search_query': search_query,
    }
    return render(request, 'social/community.html', context)

def post_detail(request, pk):
    """Public: View post details"""
    post = get_object_or_404(Post.objects.select_related('author', 'category'), pk=pk)
    comments = post.comments.select_related('author').order_by('-created_at')
    form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }
    return render(request, 'social/post_detail.html', context)

def user_profile(request, user_id):
    """Redirect to dashboard profile"""
    return redirect('dashboard:social_profile', user_id=user_id)


@login_required
def vote_post(request, pk, vote_type):
    """Public-route action for upvote/downvote while keeping dashboard/public separation."""
    post = get_object_or_404(Post, pk=pk)

    existing_vote = PostVote.objects.filter(user=request.user, post=post).first()

    if existing_vote:
        if existing_vote.vote_type == vote_type:
            if vote_type == 'upvote':
                post.upvotes = max(0, post.upvotes - 1)
            else:
                post.downvotes = max(0, post.downvotes - 1)
            existing_vote.delete()
        else:
            if vote_type == 'upvote':
                post.upvotes += 1
                post.downvotes = max(0, post.downvotes - 1)
            else:
                post.downvotes += 1
                post.upvotes = max(0, post.upvotes - 1)
            existing_vote.vote_type = vote_type
            existing_vote.save()
    else:
        PostVote.objects.create(user=request.user, post=post, vote_type=vote_type)
        if vote_type == 'upvote':
            post.upvotes += 1
        else:
            post.downvotes += 1

    post.save()
    return redirect('social:post_detail', pk=pk)
