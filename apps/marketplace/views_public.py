"""Public marketplace views - browsing and purchasing assets"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Asset, Purchase, Wishlist
from .payment import payment_processor

def marketplace_list(request):
    """Public: Browse all marketplace assets"""
    assets = Asset.objects.filter(is_active=True).select_related('seller', 'category')
    
    # Search
    search_query = request.GET.get('q', '').strip()
    if search_query:
        assets = assets.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Filter by multiple types
    asset_types = request.GET.getlist('type')
    if asset_types:
        assets = assets.filter(asset_type__in=asset_types)
    
    # Filter by price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try:
            assets = assets.filter(price__gte=float(min_price))
        except ValueError:
            pass
    if max_price:
        try:
            assets = assets.filter(price__lte=float(max_price))
        except ValueError:
            pass
    
    # Filter free assets
    if request.GET.get('free') == 'true':
        assets = assets.filter(is_free=True)
    
    # Sort
    sort = request.GET.get('sort', 'newest')
    if sort == 'price_low':
        assets = assets.order_by('price', '-created_at')
    elif sort == 'price_high':
        assets = assets.order_by('-price', '-created_at')
    elif sort == 'popular':
        assets = assets.order_by('-downloads', '-view_count')
    elif sort == 'rating':
        assets = assets.order_by('-rating', '-downloads')
    else:
        assets = assets.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(assets, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get user's wishlist asset IDs for heart button state (if authenticated)
    context = {'page_obj': page_obj}
    
    if request.user.is_authenticated:
        user_wishlist_ids = list(
            Wishlist.objects.filter(user=request.user)
                            .values_list('asset_id', flat=True)
        )
        context['user_wishlist_ids'] = user_wishlist_ids
    else:
        context['user_wishlist_ids'] = []
    
    return render(request, 'marketplace/list.html', context)

def asset_detail(request, pk):
    """Public: View asset details"""
    asset = get_object_or_404(Asset, pk=pk)
    reviews = asset.reviews.all().order_by('-created_at')
    
    return render(request, 'marketplace/detail.html', {
        'asset': asset,
        'reviews': reviews
    })

@login_required
def purchase_asset(request, pk):
    """Purchase an asset (requires login)"""
    from apps.core.notifications import send_notification
    
    asset = get_object_or_404(Asset, pk=pk)

    # Check if already purchased
    if Purchase.objects.filter(buyer=request.user, asset=asset).exists():
        messages.info(request, 'You already own this asset.')
        return redirect('marketplace:detail', pk=pk)

    # Check if free asset
    if asset.is_free or asset.price == 0:
        purchase = Purchase.objects.create(
            buyer=request.user,
            asset=asset,
            price_paid=0
        )
        asset.downloads += 1
        asset.save()
        
        # Send notification to asset seller
        send_notification(
            user=asset.seller,
            notification_type='purchase',
            title='Free Asset Downloaded!',
            message=f'{request.user.username} downloaded your asset "{asset.title}"',
            link=f'/marketplace/{asset.id}/',
            priority='normal',
            related_object_id=asset.id,
            related_object_type='asset',
            action_url=f'/dashboard/marketplace/analytics/'
        )
        
        # Send confirmation to buyer
        send_notification(
            user=request.user,
            notification_type='purchase',
            title='Asset Downloaded Successfully!',
            message=f'You have successfully downloaded "{asset.title}" by {asset.seller.username}',
            link=f'/marketplace/{asset.id}/',
            priority='normal',
            related_object_id=asset.id,
            related_object_type='asset'
        )
        
        messages.success(request, f'Successfully downloaded "{asset.title}"!')
        return redirect('marketplace:detail', pk=pk)

    # For paid assets, initiate payment
    payment_intent = payment_processor.process_asset_purchase(request.user, asset)

    if payment_intent:
        # Redirect to payment page with client secret
        return render(request, 'marketplace/payment.html', {
            'asset': asset,
            'client_secret': payment_intent.client_secret,
            'stripe_public_key': payment_processor.STRIPE_PUBLIC_KEY,
        })
    else:
        # Fallback: direct purchase (for development without Stripe)
        purchase = Purchase.objects.create(
            buyer=request.user,
            asset=asset,
            price_paid=asset.price
        )
        asset.downloads += 1
        asset.save()
        
        # Send notification to asset seller
        send_notification(
            user=asset.seller,
            notification_type='purchase',
            title='🎉 Asset Sold!',
            message=f'{request.user.username} purchased your asset "{asset.title}" for ${asset.price}',
            link=f'/marketplace/{asset.id}/',
            priority='high',
            related_object_id=asset.id,
            related_object_type='asset',
            action_url=f'/dashboard/marketplace/analytics/'
        )
        
        # Send confirmation to buyer
        send_notification(
            user=request.user,
            notification_type='purchase',
            title='Purchase Complete!',
            message=f'You have successfully purchased "{asset.title}" by {asset.seller.username} for ${asset.price}',
            link=f'/marketplace/{asset.id}/',
            priority='normal',
            related_object_id=asset.id,
            related_object_type='asset'
        )
        
        messages.warning(request, f'Payment system not configured. Asset "{asset.title}" added for testing.')
        return redirect('marketplace:detail', pk=pk)

@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    event = payment_processor.verify_webhook_signature(payload, sig_header)

    if not event:
        return JsonResponse({'error': 'Invalid signature'}, status=400)

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        transaction_id = payment_intent.get('metadata', {}).get('transaction_id')

        if transaction_id:
            payment_processor.complete_purchase(transaction_id)

    return JsonResponse({'status': 'success'})

@login_required
def payment_success(request):
    """Payment success callback"""
    messages.success(request, 'Payment successful! Your purchase is complete.')
    return redirect('marketplace:list')

@login_required
def payment_cancel(request):
    """Payment cancel callback"""
    messages.warning(request, 'Payment cancelled.')
    return redirect('marketplace:list')
