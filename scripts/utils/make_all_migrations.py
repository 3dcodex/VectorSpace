import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.core.management import call_command

print("=" * 50)
print("CREATING MIGRATIONS FOR ALL APPS")
print("=" * 50)

apps = [
    'users',
    'marketplace', 
    'games',
    'jobs',
    'mentorship',
    'competitions',
    'social',
    'workspace',
    'ai_assistant',
    'core'
]

for app in apps:
    print(f"\n📦 Making migrations for {app}...")
    try:
        call_command('makemigrations', app)
        print(f"✅ {app} migrations created")
    except Exception as e:
        print(f"⚠️ {app}: {e}")

print("\n" + "=" * 50)
print("RUNNING ALL MIGRATIONS")
print("=" * 50)
call_command('migrate')

print("\n✅ ALL DONE! Run: python manage.py runserver")
