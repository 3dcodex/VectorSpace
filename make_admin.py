import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User

username = 'admin'
user = User.objects.get(username=username)
user.profile.role = 'ADMIN'
user.is_staff = True
user.is_superuser = True
user.profile.save()
user.save()
print(f'{username} is now ADMIN with full permissions')
