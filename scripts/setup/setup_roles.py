"""
Role-Based Access Control Setup Script
Run this to apply role system migrations and create profiles for existing users
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from apps.users.models import User, UserProfile

print("=" * 60)
print("ROLE-BASED ACCESS CONTROL SETUP")
print("=" * 60)

# Apply migrations
print("\n1. Applying user migrations...")
try:
    call_command('migrate', 'users')
    print("✓ Migrations applied successfully")
except Exception as e:
    print(f"✗ Migration error: {e}")

# Create profiles for existing users without profiles
print("\n2. Creating profiles for existing users...")
users_without_profile = User.objects.filter(profile__isnull=True)
created_count = 0

for user in users_without_profile:
    UserProfile.objects.create(user=user, role='USER')
    created_count += 1
    print(f"  ✓ Created profile for: {user.username}")

if created_count == 0:
    print("  - All users already have profiles")

print(f"\n✓ Setup complete! {created_count} new profiles created")
print("\nRole System Features:")
print("  ✓ USER - Default role for all users")
print("  ✓ CREATOR - Can upload assets and games")
print("  ✓ MENTOR - Can offer mentorship sessions")
print("  ✓ RECRUITER - Can post jobs")
print("  ✓ ADMIN - Full platform access")
print("\nAccess Control:")
print("  - Asset upload restricted to CREATOR role")
print("  - Role selection available during registration")
print("  - Auto-create profile on user registration")
print("=" * 60)
