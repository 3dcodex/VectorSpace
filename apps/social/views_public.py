"""Public social views - browsing community posts and profiles"""
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count
from django.core.paginator import Paginator
from .models import Post, Category
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
