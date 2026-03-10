"""
Django signals for Vector Space.
Handles:
- Cold start bootstrap for new users
- Cache invalidation on activity changes
- Profile initialization
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from apps.users.models import User, UserProfile
from apps.marketplace.models import Asset, Purchase, Review as AssetReview
from apps.games.models import Game, GameReview
from apps.jobs.models import Job, Application
from apps.mentorship.models import MentorshipRequest, Session
from apps.core.reputation import ReputationManager
from apps.core.models import RoleProgression


@receiver(post_save, sender=UserProfile)
def initialize_profile(sender, instance, created, **kwargs):
    """
    Initialize new user profile with cold start bootstrap.
    Prevents zero scores from burying new users.
    """
    if not created:
        return
    
    profile = instance
    
    # Bootstrap score for new users in professional roles
    # This gives them initial visibility while they build real reputation
    if profile.primary_role == 'CREATOR':
        profile.creator_score = 10
        send_welcome_email(profile.user, 'creator')
    
    elif profile.primary_role == 'DEVELOPER':
        profile.developer_score = 10
        send_welcome_email(profile.user, 'developer')
    
    elif profile.primary_role == 'RECRUITER':
        profile.recruiter_score = 10
        send_welcome_email(profile.user, 'recruiter')
    
    elif profile.primary_role == 'MENTOR':
        profile.mentor_score = 10
        send_welcome_email(profile.user, 'mentor')
    
    profile.save()
    
    # Initialize role progression
    if profile.is_creator():
        RoleProgression.objects.get_or_create(
            user=profile.user,
            role='creator',
            defaults={'current_score': 10}
        )
    
    if profile.is_developer():
        RoleProgression.objects.get_or_create(
            user=profile.user,
            role='developer',
            defaults={'current_score': 10}
        )
    
    if profile.is_recruiter():
        RoleProgression.objects.get_or_create(
            user=profile.user,
            role='recruiter',
            defaults={'current_score': 10}
        )
    
    if profile.is_mentor():
        RoleProgression.objects.get_or_create(
            user=profile.user,
            role='mentor',
            defaults={'current_score': 10}
        )


@receiver(post_save, sender=Asset)
def invalidate_creator_cache_on_asset_change(sender, instance, created, **kwargs):
    """Invalidate creator reputation cache when asset status changes"""
    ReputationManager.clear_cache(instance.seller.id)


@receiver(post_save, sender=Purchase)
def invalidate_cache_on_purchase(sender, instance, created, **kwargs):
    """Invalidate caches when asset is purchased"""
    if created:
        # Invalidate both seller and buyer
        ReputationManager.clear_cache(instance.asset.seller.id)
        ReputationManager.clear_cache(instance.buyer.id)


@receiver(post_save, sender=AssetReview)
def invalidate_cache_on_asset_review(sender, instance, created, **kwargs):
    """Invalidate creator cache when asset is reviewed"""
    if created:
        ReputationManager.clear_cache(instance.asset.seller.id)


@receiver(post_save, sender=Game)
def invalidate_developer_cache_on_game(sender, instance, created, **kwargs):
    """Invalidate developer reputation cache when game is published"""
    ReputationManager.clear_cache(instance.developer.id)


@receiver(post_save, sender=GameReview)
def invalidate_cache_on_game_review(sender, instance, created, **kwargs):
    """Invalidate developer cache when game is reviewed"""
    if created:
        ReputationManager.clear_cache(instance.game.developer.id)


@receiver(post_save, sender=Job)
def invalidate_recruiter_cache_on_job(sender, instance, created, **kwargs):
    """Invalidate recruiter cache when job is posted"""
    ReputationManager.clear_cache(instance.recruiter.id)


@receiver(post_save, sender=Application)
def invalidate_cache_on_application(sender, instance, created, **kwargs):
    """Invalidate recruiter cache when application status changes"""
    ReputationManager.clear_cache(instance.job.recruiter.id)
    ReputationManager.clear_cache(instance.applicant.id)


@receiver(post_save, sender=MentorshipRequest)
def invalidate_mentor_cache_on_request(sender, instance, created, **kwargs):
    """Invalidate mentor cache when mentorship is requested"""
    ReputationManager.clear_cache(instance.mentor.id)


@receiver(post_save, sender=Session)
def invalidate_cache_on_session(sender, instance, created, **kwargs):
    """Invalidate mentor cache when session is completed"""
    ReputationManager.clear_cache(instance.request.mentor.id)
    ReputationManager.clear_cache(instance.request.mentee.id)


def send_welcome_email(user, role):
    """Send personalized welcome email based on role"""
    
    role_messages = {
        'creator': {
            'subject': '🎨 Welcome to Vector Space - Creator Edition',
            'body': f"""
Hi {user.first_name or user.username},

Welcome to Vector Space! You're now a Creator.

Your Creator Profile is live. You can start uploading and selling:
- 3D Models
- Textures
- Plugins & Scripts
- Sound Effects
- VFX & Material
- Animations

We've given you a bootstrap score of 10 to help you get started. 
As you make sales and get reviews, your score will grow.

Next steps:
1. Complete your profile
2. Upload your first asset
3. Engage with the community

Happy creating!
Vector Space Team
            """
        },
        'developer': {
            'subject': '💻 Welcome to Vector Space - Developer Edition',
            'body': f"""
Hi {user.first_name or user.username},

Welcome to Vector Space! You're now a Developer.

You can now:
- Browse and buy assets from creators
- Publish your games
- Apply for jobs
- Get mentored by experts

Your Developer Profile is ready. Start by exploring the asset marketplace.

Next steps:
1. Complete your profile
2. Browse the asset marketplace
3. Publish your first game

Let's build something amazing!
Vector Space Team
            """
        },
        'recruiter': {
            'subject': '💼 Welcome to Vector Space - Recruiter Edition',
            'body': f"""
Hi {user.first_name or user.username},

Welcome to Vector Space! You're now a Recruiter.

Talent is waiting to be discovered. You can:
- Post job openings
- Browse developer portfolios
- Manage applications
- Build your company reputation

Your Recruiter Profile is live.

Next steps:
1. Verify your company information
2. Post your first job
3. Start reviewing applications

Happy hiring!
Vector Space Team
            """
        },
        'mentor': {
            'subject': '🎓 Welcome to Vector Space - Mentor Edition',
            'body': f"""
Hi {user.first_name or user.username},

Welcome to Vector Space! You're now a Mentor.

Share your expertise with the next generation:
- Offer mentorship sessions
- Build your mentor reputation
- Connect with aspiring developers

Your Mentor Profile is ready.

Next steps:
1. Complete your profile with expertise areas
2. Set your hourly rate
3. Publish your mentorship availability

Looking forward to your impact!
Vector Space Team
            """
        }
    }
    
    if role in role_messages:
        msg = role_messages[role]
        try:
            send_mail(
                msg['subject'],
                msg['body'],
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=True,
            )
        except Exception as e:
            # Log but don't fail the signal
            import logging
            logger = logging.getLogger('signals')
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")


# Connect signals
post_save.connect(initialize_profile, sender=UserProfile)
