import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.urls import reverse, resolve
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.dashboard.views import marketplace

User = get_user_model()

def test_marketplace_routes():
    """Test all marketplace dashboard routes"""
    print("=" * 60)
    print("TESTING MARKETPLACE DASHBOARD ROUTES")
    print("=" * 60)
    
    routes = [
        ('dashboard:marketplace_dashboard', {}, 'Marketplace Dashboard'),
        ('dashboard:marketplace_browse', {}, 'Browse Marketplace'),
        ('dashboard:marketplace_my_assets', {}, 'My Assets'),
        ('dashboard:marketplace_upload', {}, 'Upload Asset'),
        ('dashboard:marketplace_purchases', {}, 'My Purchases'),
        ('dashboard:marketplace_sales', {}, 'My Sales'),
        ('dashboard:marketplace_wishlist', {}, 'My Wishlist'),
        ('dashboard:marketplace_my_collections', {}, 'My Collections'),
        ('dashboard:marketplace_create_collection', {}, 'Create Collection'),
    ]
    
    errors = []
    success = []
    
    for route_name, kwargs, description in routes:
        try:
            url = reverse(route_name, kwargs=kwargs)
            success.append(f"✓ {description}: {url}")
        except Exception as e:
            errors.append(f"✗ {description} ({route_name}): {str(e)}")
    
    print("\n✓ SUCCESSFUL ROUTES:")
    print("-" * 60)
    for s in success:
        print(s)
    
    if errors:
        print("\n✗ FAILED ROUTES:")
        print("-" * 60)
        for e in errors:
            print(e)
    else:
        print("\n✓ All routes are working correctly!")
    
    print("\n" + "=" * 60)
    return len(errors) == 0

def check_view_imports():
    """Check if all view functions exist"""
    print("\nCHECKING VIEW FUNCTIONS")
    print("=" * 60)
    
    required_views = [
        'marketplace_dashboard',
        'my_assets',
        'upload_asset',
        'edit_asset',
        'delete_asset',
        'my_purchases',
        'my_sales',
        'browse_marketplace',
        'my_wishlist',
        'add_to_wishlist',
        'remove_from_wishlist',
        'my_collections',
        'create_collection',
        'collection_detail',
        'edit_collection',
        'delete_collection',
        'add_to_collection',
        'remove_from_collection',
    ]
    
    errors = []
    success = []
    
    for view_name in required_views:
        if hasattr(marketplace, view_name):
            success.append(f"✓ {view_name}")
        else:
            errors.append(f"✗ {view_name} - NOT FOUND")
    
    for s in success:
        print(s)
    
    if errors:
        print("\n✗ MISSING VIEWS:")
        for e in errors:
            print(e)
    else:
        print("\n✓ All view functions exist!")
    
    print("=" * 60)
    return len(errors) == 0

def check_models():
    """Check if all required models exist"""
    print("\nCHECKING DATABASE MODELS")
    print("=" * 60)
    
    try:
        from apps.marketplace.models import Asset, Purchase, Review, Wishlist, Collection, CollectionItem
        
        print("✓ Asset model")
        print("✓ Purchase model")
        print("✓ Review model")
        print("✓ Wishlist model")
        print("✓ Collection model")
        print("✓ CollectionItem model")
        print("\n✓ All models are available!")
        print("=" * 60)
        return True
    except Exception as e:
        print(f"✗ Error importing models: {str(e)}")
        print("=" * 60)
        return False

def check_template():
    """Check if template file exists"""
    print("\nCHECKING TEMPLATE FILES")
    print("=" * 60)
    
    template_path = os.path.join(
        os.path.dirname(__file__),
        'templates',
        'dashboard',
        'marketplace_dashboard.html'
    )
    
    if os.path.exists(template_path):
        print(f"✓ Template exists: {template_path}")
        print("=" * 60)
        return True
    else:
        print(f"✗ Template NOT FOUND: {template_path}")
        print("=" * 60)
        return False

if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "MARKETPLACE DASHBOARD VALIDATION" + " " * 16 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    results = []
    
    # Run all checks
    results.append(("Models", check_models()))
    results.append(("Views", check_view_imports()))
    results.append(("Routes", test_marketplace_routes()))
    results.append(("Template", check_template()))
    
    # Summary
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 22 + "SUMMARY" + " " * 29 + "║")
    print("╚" + "=" * 58 + "╝")
    
    all_passed = True
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:.<40} {status}")
        if not passed:
            all_passed = False
    
    print("\n")
    if all_passed:
        print("✓✓✓ ALL CHECKS PASSED! Marketplace Dashboard is ready! ✓✓✓")
    else:
        print("✗✗✗ SOME CHECKS FAILED. Please review errors above. ✗✗✗")
    print("\n")
