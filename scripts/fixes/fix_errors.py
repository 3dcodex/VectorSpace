#!/usr/bin/env python
"""Fix all database and migration errors"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

print("=" * 50)
print("FIXING ALL ERRORS")
print("=" * 50)

# Step 1: Make migrations
print("\n1. Creating migrations...")
try:
    call_command('makemigrations')
    print("✓ Migrations created")
except Exception as e:
    print(f"✗ Error creating migrations: {e}")

# Step 2: Run migrations
print("\n2. Running migrations...")
try:
    call_command('migrate')
    print("✓ Migrations applied")
except Exception as e:
    print(f"✗ Error running migrations: {e}")

print("\n" + "=" * 50)
print("DONE! Restart your server.")
print("=" * 50)
