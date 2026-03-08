import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.core.management import call_command

print("=" * 50)
print("VECTOR SPACE - DATABASE SETUP")
print("=" * 50)
print()

print("Step 1: Making migrations...")
try:
    call_command('makemigrations')
    print("✅ Migrations created successfully!")
except Exception as e:
    print(f"⚠️ Error creating migrations: {e}")
print()

print("Step 2: Running migrations...")
try:
    call_command('migrate')
    print("✅ Database migrated successfully!")
except Exception as e:
    print(f"❌ Error migrating database: {e}")
print()

print("=" * 50)
print("DATABASE SETUP COMPLETE!")
print("=" * 50)
print()
print("You can now run: python manage.py runserver")
print()
