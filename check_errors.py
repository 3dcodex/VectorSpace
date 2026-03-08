import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.urls import reverse
from django.core.management import call_command

print("Checking for errors...\n")

# Check URLs
print("1. Testing URL patterns...")
try:
    reverse('dashboard:overview')
    print("   ✓ dashboard:overview")
except Exception as e:
    print(f"   ✗ dashboard:overview - {e}")

try:
    reverse('dashboard:marketplace_my_assets')
    print("   ✓ dashboard:marketplace_my_assets")
except Exception as e:
    print(f"   ✗ dashboard:marketplace_my_assets - {e}")

try:
    reverse('dashboard:marketplace_dashboard')
    print("   ✓ dashboard:marketplace_dashboard")
except Exception as e:
    print(f"   ✗ dashboard:marketplace_dashboard - {e}")

# Check models
print("\n2. Testing model imports...")
try:
    from apps.marketplace.models import Asset, Purchase, Review
    print("   ✓ Marketplace models")
except Exception as e:
    print(f"   ✗ Marketplace models - {e}")

try:
    from apps.games.models import Game
    print("   ✓ Game model")
except Exception as e:
    print(f"   ✗ Game model - {e}")

try:
    from apps.social.models import Post
    print("   ✓ Post model")
except Exception as e:
    print(f"   ✗ Post model - {e}")

# Check templates
print("\n3. Checking templates...")
templates = [
    'templates/dashboard/overview.html',
    'templates/marketplace/my_assets.html',
    'templates/dashboard/marketplace_dashboard.html',
]

for template in templates:
    path = os.path.join(os.path.dirname(__file__), template)
    if os.path.exists(path):
        print(f"   ✓ {template}")
    else:
        print(f"   ✗ {template} - NOT FOUND")

# Check for syntax errors
print("\n4. Running Django checks...")
try:
    call_command('check', '--deploy')
    print("   ✓ No deployment issues")
except Exception as e:
    print(f"   ✗ Issues found: {e}")

print("\n✓ Error check complete!")
