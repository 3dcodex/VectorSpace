import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import reverse

# Test URL reversing
urls_to_test = [
    'home',
    'marketplace:list',
    'games:list',
    'jobs:list',
    'social:community',
    'competitions:list',
    'mentorship:list',
    'users:login',
    'users:signup',
]

print("Testing URL reversing:")
for url_name in urls_to_test:
    try:
        url = reverse(url_name)
        print(f"✓ {url_name:30} -> {url}")
    except Exception as e:
        print(f"✗ {url_name:30} -> ERROR: {e}")
