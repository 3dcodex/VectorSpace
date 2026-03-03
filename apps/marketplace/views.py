from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Asset, Purchase, Review, Transaction
from .forms import AssetUploadForm
from .payment import payment_processor
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Asset, Purchase, Review
from .forms import AssetUploadForm

@login_required
def upload_asset(request):
    if request.user.profile.role != 'CREATOR':
        messages.error(request, 'Only creators can upload assets. Please update your profile role.')
        return redirect('users:dashboard')
    
    if request.method == 'POST':
        form = AssetUploadForm(request.POST, request.FILES)
        if form.is_valid():
            asset = form.save(commit=False)
            asset.seller = request.user
            asset.save()
            
            messages.success(request, f'"{asset.title}" uploaded successfully and is now live!')
            return redirect('marketplace:my_assets')
    else:
        form = AssetUploadForm()
    
    return render(request, 'marketplace/upload.html', {'form': form})

@login_required
def my_assets(request):
    if request.user.profile.role != 'CREATOR':
        return redirect('users:dashboard')
    
    assets = Asset.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'marketplace/my_assets.html', {'assets': assets})

@login_required
def edit_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        form = AssetUploadForm(request.POST, request.FILES, instance=asset)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{asset.title}" updated successfully!')
            return redirect('marketplace:my_assets')
    else:
        form = AssetUploadForm(instance=asset)
    
    return render(request, 'marketplace/edit_asset.html', {'form': form, 'asset': asset})

@login_required
def delete_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk, seller=request.user)
    
    if request.method == 'POST':
        title = asset.title
        asset.delete()
        messages.success(request, f'"{title}" deleted successfully!')
        return redirect('marketplace:my_assets')
    
    return render(request, 'marketplace/delete_confirm.html', {'asset': asset})

from django.core.paginator import Paginator
from django.db.models import Q

def marketplace_list(request):
    assets = Asset.objects.all()
    
    # Search
    search_query = request.GET.get('q')
    if search_query:
        assets = assets.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Filter by type
    asset_type = request.GET.get('type')
    if asset_type:
        assets = assets.filter(asset_type=asset_type)
    
    # Filter by price
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        assets = assets.filter(price__gte=min_price)
    if max_price:
        assets = assets.filter(price__lte=max_price)
    
    # Filter free assets
    if request.GET.get('free') == 'true':
        assets = assets.filter(is_free=True)
    
    # Sort
    sort = request.GET.get('sort')
    if sort == 'price_low':
        assets = assets.order_by('price')
    elif sort == 'price_high':
        assets = assets.order_by('-price')
    elif sort == 'popular':
        assets = assets.order_by('-downloads')
    else:
        assets = assets.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(assets, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'marketplace/list.html', {'page_obj': page_obj, 'assets': assets})

def asset_detail(request, pk):
    asset = get_object_or_404(Asset, pk=pk)
    reviews = asset.reviews.all().order_by('-created_at')
    
    return render(request, 'marketplace/detail.html', {
        'asset': asset,
        'reviews': reviews
    })

@login_required
def purchase_asset(request, pk):
    asset = get_object_or_404(Asset, pk=pk)

    # Check if already purchased
    if Purchase.objects.filter(buyer=request.user, asset=asset).exists():
        messages.info(request, 'You already own this asset.')
        return redirect('marketplace:asset_detail', pk=pk)

    # Check if free asset
    if asset.is_free or asset.price == 0:
        Purchase.objects.create(
            buyer=request.user,
            asset=asset,
            price_paid=0
        )
        asset.downloads += 1
        asset.save()
        messages.success(request, f'Successfully downloaded "{asset.title}"!')
        return redirect('marketplace:asset_detail', pk=pk)

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
        Purchase.objects.create(
            buyer=request.user,
            asset=asset,
            price_paid=asset.price
        )
        asset.downloads += 1
        asset.save()
        messages.warning(request, f'Payment system not configured. Asset "{asset.title}" added for testing.')
        return redirect('marketplace:asset_detail', pk=pk)
@csrf_exempt
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    import json

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
    messages.success(request, 'Payment successful! Your purchase is complete.')
    return redirect('marketplace:list')

@login_required
def payment_cancel(request):
    messages.warning(request, 'Payment cancelled.')
    return redirect('marketplace:list')
