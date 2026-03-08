import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'admin'
password = 'admin'
email = 'admin@vectorspace.com'

if User.objects.filter(username=username).exists():
    print(f"✅ User '{username}' already exists!")
else:
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"✅ Superuser created!")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"   Email: {email}")
