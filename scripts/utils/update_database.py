#!/usr/bin/env python
"""
Database Update Script
Handles migrations for new features added to Vector Space
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def check_database():
    """Check if database exists and is accessible"""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def create_migrations():
    """Create migrations for all apps"""
    apps = [
        'users',
        'marketplace',
        'games',
        'social',
        'jobs',
        'mentorship',
        'competitions',
        'workspace',
        'ai_assistant',
        'core',
    ]
    
    print("\n=== Creating Migrations ===")
    for app in apps:
        try:
            print(f"Creating migrations for {app}...")
            call_command('makemigrations', app, interactive=False)
        except Exception as e:
            print(f"Warning: {app} - {e}")
    
    print("✓ Migrations created")

def apply_migrations():
    """Apply all migrations"""
    print("\n=== Applying Migrations ===")
    try:
        call_command('migrate', interactive=False)
        print("✓ Migrations applied successfully")
        return True
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False

def create_superuser_prompt():
    """Prompt to create superuser"""
    print("\n=== Superuser Setup ===")
    response = input("Would you like to create a superuser? (y/n): ")
    if response.lower() == 'y':
        try:
            call_command('createsuperuser')
        except Exception as e:
            print(f"Superuser creation skipped: {e}")

def show_summary():
    """Show summary of new features"""
    print("\n" + "="*60)
    print("DATABASE UPDATE COMPLETE!")
    print("="*60)
    print("\nNew Features Added:")
    print("  ✓ Post voting system (upvote/downvote)")
    print("  ✓ Game reviews and comments")
    print("  ✓ Payment integration (Stripe)")
    print("  ✓ Transaction and wallet management")
    print("  ✓ Analytics dashboard")
    print("  ✓ Content reporting system")
    print("  ✓ Moderation dashboard")
    print("\nNext Steps:")
    print("  1. Configure Stripe API keys in .env")
    print("  2. Run: python manage.py runserver")
    print("  3. Visit: http://localhost:8000")
    print("  4. Check SETUP_GUIDE.md for detailed instructions")
    print("\nFor moderation features:")
    print("  - Login as superuser")
    print("  - Access moderation dashboard from user dashboard")
    print("="*60 + "\n")

def main():
    """Main execution"""
    print("="*60)
    print("VECTOR SPACE - DATABASE UPDATE")
    print("="*60)
    
    # Check database connection
    if not check_database():
        print("\nPlease ensure your database is configured correctly.")
        sys.exit(1)
    
    # Create migrations
    create_migrations()
    
    # Apply migrations
    if not apply_migrations():
        print("\nMigration failed. Please check the error messages above.")
        sys.exit(1)
    
    # Prompt for superuser
    create_superuser_prompt()
    
    # Show summary
    show_summary()

if __name__ == '__main__':
    main()
