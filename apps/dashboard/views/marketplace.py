from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg, Max
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from apps.marketplace.models import Asset, Purchase, Wishlist, Collection, CollectionItem, Review
from apps.marketplace.forms import AssetUploadForm
from apps.users.models import User

@login_required
def marketplace_dashboard(request):
    """Role-based marketplace view - Creator dashboard or Buyer storefront"""
    user = request.user
    is_creator = user.profile.role in ['CREATOR', 'ADMIN']
    
    if is_creator:
        # Creator Dashboard
        my_assets = Asset.objects.filter(seller=user).order_by('-created_at')[:6]
        total_assets = Asset.objects.filter(seller=user).count()
        total_downloads = Asset.objects.filter(seller=user).aggregate(total=Sum('downloads'))['total'] or 0
        sales = Purchase.objects.filter(asset__seller=user)
        total_sales = sales.count()
        total_revenue = sales.aggregate(total=Sum('price_paid'))['total'] or 0
        recent_sales = sales.select_related('buyer', 'asset').order_by('-purchased_at')[:5]
        
        now = timezone.now()
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        revenue_this_month = sales.filter(purchased_at__gte=this_month_start).aggregate(total=Sum('price_paid'))['total'] or 0
        avg_rating = Asset.objects.filter(seller=user).aggregate(avg=Avg('rating'))['avg'] or 0
        top_assets = Asset.objects.filter(seller=user).annotate(sales_count=Count('purchase')).order_by('-sales_count')[:3]
        recent_reviews = Review.objects.filter(asset__seller=user).select_related('user', 'asset').order_by('-created_at')[:5]
        
        context = {
            'is_creator': True,
            'my_assets': my_assets,
            'total_assets': total_assets,
            'total_downloads': total_downloads,
            'total_sales': total_sales,
            'total_revenue': total_revenue,
            'revenue_this_month': revenue_this_month,
            'avg_rating': avg_rating,
            'recent_sales': recent_sales,
            'top_assets': top_assets,
            'recent_reviews': recent_reviews,
        }
        return render(request, 'dashboard/marketplace_dashboard.html', context)
    else:
        # Buyer Storefront
        featured_assets = Asset.objects.filter(is_active=True).order_by('-downloads')[:8]
        categories = Asset.ASSET_TYPES
        my_purchases = Purchase.objects.filter(buyer=user).count()
        wishlist_count = Wishlist.objects.filter(user=user).count()
        
        context = {
            'is_creator': False,
            'featured_assets': featured_assets,
            'categories': categories,
            'my_purchases': my_purchases,
            'wishlist_count': wishlist_count,
        }
        return render(request, 'marketplace/buyer_storefront.html', context)

@login_required
def my_assets(request):
    """List user's uploaded assets with comprehensive stats and insights"""
    user = request.user
    assets = Asset.objects.filter(seller=user).order_by('-created_at')
    
    total_assets = assets.count()
    total_downloads = assets.aggregate(total=Sum('downloads'))['total'] or 0
    total_sales = Purchase.objects.filter(asset__seller=user).count()
    total_revenue = Purchase.objects.filter(asset__seller=user).aggregate(total=Sum('price_paid'))['total'] or 0
    avg_rating = assets.aggregate(avg=Avg('rating'))['avg'] or 0
    
    context = {
        'assets': assets,
        'total_assets': total_assets,
        'total_downloads': total_downloads,
        'total_sales': total_sales,
        'total_revenue': total_revenue,
        'avg_rating': avg_rating,
    }
    
    return render(request, 'marketplace/my_assets.html', context)

@login_required
def upload_asset(request):
    """Upload a new asset"""
    if request.user.profile.role not in ['CREATOR', 'ADMIN']:
        messages.info(request, 'You need to be a Creator to upload assets. Contact support to upgrade your account.')
        return redirect('dashboard:overview')
    
    if request.method == 'POST':
        form = AssetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.seller = request.user
            asset.save()
            
            messages.success(request, f'"{asset.title}" uploaded successfully and is now live!')
            return redirect('dashboard:marketplace_my_assets')
    else:
        form = AssetUploadForm()
    
    return render(request, 'marketplace/upload.html', {'form': form})

@login_required
def edit_asset(request, pk):
    """Edit an existing asset"""
    asset = get_object_or_404(Asset, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        form = AssetUploadForm(request.POST, request.FILES, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{asset.title}" updated successfully!')
            return redirect('dashboard:marketplace_my_assets')
    else:
        form = AssetUploadForm(instance=asset)
    
    return render(request, 'marketplace/edit_asset.html', {'form': form, 'asset': asset})

@login_required
def delete_asset(request, pk):
    """Delete an asset"""
    asset = get_object_or_404(Asset, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        title = asset.title
        asset.delete()
        messages.success(request, f'"{title}" deleted successfully!')
        return redirect('dashboard:marketplace_my_assets')
    
    return render(request, 'marketplace/delete_confirm.html', {'asset': asset})

@login_required
def my_purchases(request):
    """List user's purchased assets"""
    purchases = Purchase.objects.filter(buyer=request.user).order_by('-purchased_at')
    return render(request, 'marketplace/my_purchases.html', {'purchases': purchases})

@login_required
def my_sales(request):
    """List sales of user's assets"""
    sales = Purchase.objects.filter(asset__seller=request.user).order_by('-purchased_at')
    return render(request, 'marketplace/my_sales.html', {'sales': sales})

@login_required
def browse_marketplace(request):
    """Browse marketplace assets with search, category, and sort filters"""
    assets = Asset.objects.filter(is_active=True)

    search_query = request.GET.get('q', '').strip()
    if search_query:
        assets = assets.filter(
            Q(title__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(tags__icontains=search_query)
        )

    asset_type = request.GET.get('type', '').strip()
    if asset_type:
        assets = assets.filter(asset_type=asset_type)

    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    if min_price:
        assets = assets.filter(price__gte=min_price)
    if max_price:
        assets = assets.filter(price__lte=max_price)

    if request.GET.get('free') == 'true':
        assets = assets.filter(is_free=True)

    sort = request.GET.get('sort', 'popular')
    if sort == 'price_low':
        assets = assets.order_by('price', '-created_at')
    elif sort == 'price_high':
        assets = assets.order_by('-price', '-created_at')
    elif sort == 'newest':
        assets = assets.order_by('-created_at')
    else:
        assets = assets.order_by('-downloads', '-created_at')

    featured_assets = assets[:12]

    return render(
        request,
        'dashboard/marketplace_browse.html',
        {
            'featured_assets': featured_assets,
            'asset_type_choices': Asset.ASSET_TYPES,
            'current_filters': {
                'q': search_query,
                'type': asset_type,
                'min_price': min_price,
                'max_price': max_price,
                'free': request.GET.get('free', ''),
                'sort': sort,
            },
        },
    )


# ===============================
# WISHLIST MANAGEMENT VIEWS
# ===============================

@login_required
def my_wishlist(request):
    """Display user's wishlist with filtering and sorting options"""
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('asset', 'asset__seller')
    
    # Search functionality
    search_query = request.GET.get('q', '').strip()
    if search_query:
        wishlist_items = wishlist_items.filter(
            Q(asset__title__icontains=search_query) |
            Q(asset__description__icontains=search_query) |
            Q(asset__tags__icontains=search_query)
        )
    
    # Filter by asset type
    asset_type = request.GET.get('type', '').strip()
    if asset_type:
        wishlist_items = wishlist_items.filter(asset__asset_type=asset_type)
    
    # Sorting options
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        wishlist_items = wishlist_items.order_by('asset__price')
    elif sort == 'price_high':
        wishlist_items = wishlist_items.order_by('-asset__price')
    elif sort == 'alphabetical':
        wishlist_items = wishlist_items.order_by('asset__title')
    else:  # newest (default)
        wishlist_items = wishlist_items.order_by('-added_at')
    
    # Get user's collections for the "Add to Collection" dropdown
    user_collections = Collection.objects.filter(owner=request.user).order_by('name')
    
    context = {
        'wishlist_items': wishlist_items,
        'user_collections': user_collections,
        'asset_type_choices': Asset.ASSET_TYPES,
        'current_filters': {
            'q': search_query,
            'type': asset_type,
            'sort': sort,
        },
    }
    return render(request, 'marketplace/wishlist.html', context)


@require_POST
@login_required
def add_to_wishlist(request, asset_id):
    """AJAX endpoint to add asset to user's wishlist"""
    try:
        asset = get_object_or_404(Asset, id=asset_id, is_active=True)
        
        # Check if already in wishlist
        wishlist_item, created = Wishlist.objects.get_or_create(
            user=request.user,
            asset=asset
        )
        
        if created:
            return JsonResponse({
                'success': True,
                'message': f'"{asset.title}" added to your wishlist!',
                'in_wishlist': True
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Asset is already in your wishlist.',
                'in_wishlist': True
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Failed to add to wishlist. Please try again.',
            'error': str(e)
        })


@require_POST
@login_required
def remove_from_wishlist(request, asset_id):
    """AJAX endpoint to remove asset from user's wishlist"""
    try:
        asset = get_object_or_404(Asset, id=asset_id)
        
        wishlist_item = Wishlist.objects.filter(
            user=request.user,
            asset=asset
        ).first()
        
        if wishlist_item:
            wishlist_item.delete()
            return JsonResponse({
                'success': True,
                'message': f'"{asset.title}" removed from your wishlist.',
                'in_wishlist': False
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Asset was not in your wishlist.',
                'in_wishlist': False
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Failed to remove from wishlist. Please try again.',
            'error': str(e)
        })


# ===============================
# COLLECTION MANAGEMENT VIEWS
# ===============================

@login_required
def my_collections(request):
    """List all collections owned by the user"""
    collections = Collection.objects.filter(owner=request.user).annotate(
        asset_count=Count('items')
    ).order_by('-updated_at')
    
    search_query = request.GET.get('q', '').strip()
    if search_query:
        collections = collections.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    context = {
        'collections': collections,
        'search_query': search_query,
    }
    return render(request, 'marketplace/collections.html', context)


@login_required
def create_collection(request):
    """Create a new collection"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        is_public = request.POST.get('is_public') == 'on'
        
        if not name:
            messages.error(request, 'Collection name is required.')
            return redirect('marketplace_create_collection')
        
        # Check if user already has a collection with this name
        if Collection.objects.filter(owner=request.user, name__iexact=name).exists():
            messages.error(request, f'You already have a collection named "{name}". Please choose a different name.')
            return redirect('marketplace_create_collection')
        
        try:
            collection = Collection.objects.create(
                name=name,
                description=description,
                owner=request.user,
                is_public=is_public
            )
            
            messages.success(request, f'Collection "{collection.name}" created successfully!')
            return redirect('marketplace_collection_detail', username=request.user.username, slug=collection.slug)
            
        except Exception as e:
            messages.error(request, f'Failed to create collection: {str(e)}')
            return redirect('marketplace_create_collection')
    
    return render(request, 'marketplace/create_collection.html')


@login_required
def collection_detail(request, username, slug):
    """View a specific collection"""
    # Get the collection owner
    owner = get_object_or_404(User, username=username)
    collection = get_object_or_404(Collection, owner=owner, slug=slug)
    
    # Privacy check - only owner can view private collections
    if not collection.is_public and collection.owner != request.user:
        messages.error(request, 'This collection is private.')
        return redirect('marketplace_my_collections')
    
    # Get collection items with related data
    collection_items = CollectionItem.objects.filter(collection=collection)\
        .select_related('asset', 'asset__seller')\
        .order_by('position', '-added_at')
    
    # Search functionality within collection
    search_query = request.GET.get('q', '').strip()
    if search_query:
        collection_items = collection_items.filter(
            Q(asset__title__icontains=search_query) |
            Q(asset__description__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    
    # Get user's other collections if viewing own collection
    other_collections = []
    if collection.owner == request.user:
        other_collections = Collection.objects.filter(owner=request.user)\
            .exclude(id=collection.id).order_by('name')
    
    is_owner = collection.owner == request.user
    
    context = {
        'collection': collection,
        'collection_items': collection_items,
        'other_collections': other_collections,
        'is_owner': is_owner,
        'search_query': search_query,
    }
    return render(request, 'marketplace/collection_detail.html', context)


@login_required 
def edit_collection(request, username, slug):
    """Edit collection details"""
    collection = get_object_or_404(Collection, owner=request.user, slug=slug)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        is_public = request.POST.get('is_public') == 'on'
        
        if not name:
            messages.error(request, 'Collection name is required.')
        else:
            # Check for duplicate names (excluding current collection)
            if Collection.objects.filter(owner=request.user, name__iexact=name)\
                .exclude(id=collection.id).exists():
                messages.error(request, f'You already have a collection named "{name}". Please choose a different name.')
            else:
                try:
                    collection.name = name
                    collection.description = description
                    collection.is_public = is_public
                    collection.save()  # This will regenerate slug if needed
                    
                    messages.success(request, 'Collection updated successfully!')
                    return redirect('marketplace_collection_detail', username=request.user.username, slug=collection.slug)
                    
                except Exception as e:
                    messages.error(request, f'Failed to update collection: {str(e)}')
    
    context = {
        'collection': collection,
    }
    return render(request, 'marketplace/edit_collection.html', context)


@login_required
def delete_collection(request, username, slug):
    """Delete a collection"""
    collection = get_object_or_404(Collection, owner=request.user, slug=slug)
    
    if request.method == 'POST':
        name = collection.name
        collection.delete()
        messages.success(request, f'Collection "{name}" deleted successfully!')
        return redirect('marketplace_my_collections')
    
    # Count items for confirmation message
    item_count = CollectionItem.objects.filter(collection=collection).count()
    
    context = {
        'collection': collection,
        'item_count': item_count,
    }
    return render(request, 'marketplace/delete_collection_confirm.html', context)


@require_POST
@login_required
def add_to_collection(request, collection_id, asset_id):
    """AJAX endpoint to add asset to a collection"""
    try:
        collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
        asset = get_object_or_404(Asset, id=asset_id, is_active=True)
        
        # Check if asset is already in this collection
        existing_item = CollectionItem.objects.filter(collection=collection, asset=asset).first()
        if existing_item:
            return JsonResponse({
                'success': False,
                'message': f'"{asset.title}" is already in "{collection.name}".'
            })
        
        # Get notes if provided
        notes = request.POST.get('notes', '').strip()
        
        # Add to collection at the end (highest position)
        last_position = CollectionItem.objects.filter(collection=collection)\
            .aggregate(max_pos=models.Max('position'))['max_pos'] or 0
        
        CollectionItem.objects.create(
            collection=collection,
            asset=asset,
            position=last_position + 1,
            notes=notes
        )
        
        return JsonResponse({
            'success': True,
            'message': f'"{asset.title}" added to "{collection.name}"!',
            'collection_url': collection.get_absolute_url()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Failed to add to collection. Please try again.',
            'error': str(e)
        })


@require_POST
@login_required
def remove_from_collection(request, collection_id, asset_id):
    """AJAX endpoint to remove asset from a collection"""
    try:
        collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
        asset = get_object_or_404(Asset, id=asset_id)
        
        collection_item = CollectionItem.objects.filter(
            collection=collection, 
            asset=asset
        ).first()
        
        if collection_item:
            collection_item.delete()
            return JsonResponse({
                'success': True,
                'message': f'"{asset.title}" removed from "{collection.name}".'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Asset was not found in this collection.'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Failed to remove from collection. Please try again.',
            'error': str(e)
        })


@require_POST
@login_required
def update_collection_item_notes(request, collection_id, asset_id):
    """AJAX endpoint to update notes for a collection item"""
    try:
        collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
        asset = get_object_or_404(Asset, id=asset_id)
        
        collection_item = get_object_or_404(
            CollectionItem, 
            collection=collection, 
            asset=asset
        )
        
        notes = request.POST.get('notes', '').strip()
        collection_item.notes = notes
        collection_item.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Notes updated successfully!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Failed to update notes. Please try again.',
            'error': str(e)
        })


