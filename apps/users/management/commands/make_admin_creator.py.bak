from django.core.management.base import BaseCommand
from apps.users.models import User

class Command(BaseCommand):
    help = 'Make user admin creator'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            user.profile.role = 'ADMIN'
            user.is_staff = True
            user.is_superuser = True
            user.profile.save()
            user.save()
            self.stdout.write(self.style.SUCCESS(f'{username} is now ADMIN'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} not found'))
