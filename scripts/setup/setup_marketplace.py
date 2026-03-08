"""
Marketplace Model Setup Script
Run this after updating the Asset model to apply migrations
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

print("=" * 60)
print("MARKETPLACE MODEL SETUP")
print("=" * 60)

# Apply migrations
print("\n1. Applying marketplace migrations...")
try:
    call_command('migrate', 'marketplace')
    print("✓ Migrations applied successfully")
except Exception as e:
    print(f"✗ Migration error: {e}")

# Create sample categories
print("\n2. Creating sample categories...")
from apps.marketplace.models import Category

categories = ['Characters', 'Environments', 'Props', 'Vehicles', 'Weapons', 'Architecture']
created_count = 0

for cat_name in categories:
    category, created = Category.objects.get_or_create(name=cat_name)
    if created:
        created_count += 1
        print(f"  ✓ Created: {cat_name}")
    else:
        print(f"  - Exists: {cat_name}")

print(f"\n✓ Setup complete! {created_count} new categories created")
print("\nYou can now:")
print("  - Upload assets via /marketplace/upload/")
print("  - Browse marketplace at /marketplace/")
print("  - Manage categories in admin panel")
print("=" * 60)
