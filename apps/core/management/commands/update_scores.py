"""
Management command to update all user reputation scores.
Usage: python manage.py update_scores
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from apps.core.reputation import ReputationManager
import time


class Command(BaseCommand):
    help = 'Update all user reputation scores'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            help='Update score for specific user ID only',
        )
    
    def handle(self, *args, **options):
        verbose = options['verbose']
        user_id = options.get('user_id')
        
        start_time = time.time()
        
        if user_id:
            # Update single user
            from apps.users.models import User
            try:
                user = User.objects.get(id=user_id)
                profile = user.profile
                
                self.stdout.write(f"Updating scores for {user.username}...")
                
                if profile.is_creator():
                    score = ReputationManager.get_creator_score(user)
                    profile.creator_score = score
                    self.stdout.write(f"  Creator: {score}/100")
                
                if profile.is_developer():
                    score = ReputationManager.get_developer_score(user)
                    profile.developer_score = score
                    self.stdout.write(f"  Developer: {score}/100")
                
                if profile.is_recruiter():
                    score = ReputationManager.get_recruiter_score(user)
                    profile.recruiter_score = score
                    self.stdout.write(f"  Recruiter: {score}/100")
                
                if profile.is_mentor():
                    score = ReputationManager.get_mentor_score(user)
                    profile.mentor_score = score
                    self.stdout.write(f"  Mentor: {score}/100")
                
                profile.save()
                
                elapsed = time.time() - start_time
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Updated {user.username} in {elapsed:.2f}s'
                    )
                )
            
            except User.DoesNotExist:
                raise CommandError(f'User with id {user_id} not found')
        
        else:
            # Update all users
            self.stdout.write('Updating all user reputation scores...')
            result = ReputationManager.update_all_scores()
            elapsed = time.time() - start_time
            
            self.stdout.write(self.style.SUCCESS(
                f'✓ {result} in {elapsed:.2f}s'
            ))
            
            if verbose:
                self.stdout.write(f"\nDetails:")
                self.stdout.write(f"  Total time: {elapsed:.2f}s")
                self.stdout.write(f"  Completed at: {timezone.now().isoformat()}")
