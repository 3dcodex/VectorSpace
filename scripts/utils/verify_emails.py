import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Verify all users
User.objects.all().update(email_verified=True)

print("✅ All users email verified!")
print(f"   Total users: {User.objects.count()}")
