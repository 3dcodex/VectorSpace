"""
Reputation management system for Vector Space.
Calculates and caches user reputation scores across roles.
Caching: 24-hour TTL via Redis or in-memory cache.
"""

from django.db.models import Sum, Avg, Count
from django.utils import timezone
from django.core.cache import cache
from datetime import timedelta
from decimal import Decimal


class ReputationManager:
    """
    Calculates role-specific reputation scores for users.
    Uses caching to avoid repeated database queries.
    Run daily via Celery task for efficiency.
    """
    
    CACHE_TTL = 86400  # 24 hours
    TRUST_LEVELS = {
        'bronze': (0, 25),
        'silver': (25, 50),
        'gold': (50, 75),
        'platinum': (75, 90),
        'elite': (90, 100),
    }
    
    @staticmethod
    def get_creator_score(user):
        """
        Creator Score: Asset quality and sales
        
        Weighted formula:
        - Download count (30%): volume
        - Average rating (40%): quality
        - Sales volume (20%): monetization
        - Review count (10%): engagement
        
        Scale: 0-100
        """
        # Check cache first
        cache_key = f'creator_score_{user.id}'
        cached_score = cache.get(cache_key)
        if cached_score is not None:
            return cached_score
        
        from apps.marketplace.models import Asset, Purchase, Review as AssetReview
        
        profile = user.profile
        assets = Asset.objects.filter(seller=user)
        
        if not assets.exists():
            cache.set(cache_key, 0, ReputationManager.CACHE_TTL)
            return 0
        
        # 1. Download performance (0-30 points)
        total_downloads = assets.aggregate(Sum('downloads'))['downloads__sum'] or 0
        download_score = min(30, (total_downloads / 1000) * 30)
        
        # 2. Rating quality (0-40 points)
        avg_rating = assets.aggregate(Avg('rating'))['rating__avg'] or 0
        rating_score = (avg_rating / 5.0) * 40
        
        # 3. Sales volume (0-20 points)
        total_sales = Purchase.objects.filter(asset__seller=user).count()
        sales_score = min(20, (total_sales / 100) * 20)
        
        # 4. Review engagement (0-10 bonus points)
        review_count = AssetReview.objects.filter(asset__seller=user).count()
        review_score = min(10, review_count * 0.5)
        
        creator_score = round(min(100, download_score + rating_score + sales_score + review_score), 2)
        
        # Update profile metadata
        profile.creator_sales_count = total_sales
        profile.creator_total_revenue = Purchase.objects.filter(
            asset__seller=user
        ).aggregate(total=Sum('price_paid'))['total'] or Decimal('0.00')
        profile.save(update_fields=['creator_sales_count', 'creator_total_revenue'])
        
        # Cache result
        cache.set(cache_key, creator_score, ReputationManager.CACHE_TTL)
        return creator_score
    
    @staticmethod
    def get_developer_score(user):
        """
        Developer Score: Game quality and reach
        
        Weighted formula:
        - Game downloads (40%): reach
        - Average rating (40%): quality
        - Published games (10%): consistency
        - Engagement (10%): community
        
        Scale: 0-100
        """
        # Check cache
        cache_key = f'developer_score_{user.id}'
        cached_score = cache.get(cache_key)
        if cached_score is not None:
            return cached_score
        
        from apps.games.models import Game, GameReview
        
        profile = user.profile
        games = Game.objects.filter(developer=user, status='published')
        
        if not games.exists():
            cache.set(cache_key, 0, ReputationManager.CACHE_TTL)
            return 0
        
        # 1. Download performance (0-40 points)
        total_downloads = games.aggregate(Sum('downloads'))['downloads__sum'] or 0
        download_score = min(40, (total_downloads / 5000) * 40)
        
        # 2. Rating quality (0-40 points)
        avg_rating = games.aggregate(Avg('rating'))['rating__avg'] or 0
        rating_score = (avg_rating / 5.0) * 40
        
        # 3. Game library size (0-10 points)
        game_count = games.count()
        library_score = min(10, game_count)
        
        # 4. Engagement via reviews (0-10 bonus points)
        review_count = GameReview.objects.filter(game__developer=user).count()
        engagement_score = min(10, review_count * 0.2)
        
        developer_score = round(min(100, download_score + rating_score + library_score + engagement_score), 2)
        
        # Update metadata
        profile.developer_games_published = games.count()
        profile.developer_total_downloads = total_downloads
        profile.save(update_fields=['developer_games_published', 'developer_total_downloads'])
        
        # Cache
        cache.set(cache_key, developer_score, ReputationManager.CACHE_TTL)
        return developer_score
    
    @staticmethod
    def get_recruiter_score(user):
        """
        Recruiter Score: Hiring success
        
        Weighted formula:
        - Successful hires (50%): primary metric
        - Application response rate (30%): professionalism
        - Active job postings (20%): consistency
        
        Scale: 0-100
        """
        # Check cache
        cache_key = f'recruiter_score_{user.id}'
        cached_score = cache.get(cache_key)
        if cached_score is not None:
            return cached_score
        
        from apps.jobs.models import Job, Application
        
        profile = user.profile
        jobs = Job.objects.filter(recruiter=user)
        
        if not jobs.exists():
            cache.set(cache_key, 0, ReputationManager.CACHE_TTL)
            return 0
        
        # 1. Successful hires (0-50 points)
        successful_hires = profile.recruiter_successful_hires
        hire_score = min(50, successful_hires)
        
        # 2. Response rate (0-30 points)
        total_applications = Application.objects.filter(job__recruiter=user).count()
        responded = Application.objects.filter(
            job__recruiter=user
        ).exclude(status='pending').count()
        
        if total_applications > 0:
            response_rate = responded / total_applications
            response_score = response_rate * 30
        else:
            response_score = 0
        
        # 3. Active job posting consistency (0-20 points)
        active_jobs = profile.recruiter_active_jobs
        posting_score = min(20, active_jobs * 2)
        
        recruiter_score = round(min(100, hire_score + response_score + posting_score), 2)
        
        # Cache
        cache.set(cache_key, recruiter_score, ReputationManager.CACHE_TTL)
        return recruiter_score
    
    @staticmethod
    def get_mentor_score(user):
        """
        Mentor Score: Teaching effectiveness
        
        Weighted formula:
        - Sessions completed (40%): consistency
        - Student satisfaction (40%): quality
        - Unique student count (20%): reach
        
        Scale: 0-100
        """
        # Check cache
        cache_key = f'mentor_score_{user.id}'
        cached_score = cache.get(cache_key)
        if cached_score is not None:
            return cached_score
        
        from apps.mentorship.models import MentorshipRequest
        
        profile = user.profile
        requests = MentorshipRequest.objects.filter(mentor=user, status='accepted')
        
        if not requests.exists():
            cache.set(cache_key, 0, ReputationManager.CACHE_TTL)
            return 0
        
        # 1. Completed sessions (0-40 points)
        sessions_completed = profile.mentor_sessions_completed
        session_score = min(40, (sessions_completed / 50) * 40)
        
        # 2. Student satisfaction (0-40 points) - default to 3.0/5
        avg_satisfaction = 3.0
        satisfaction_score = (avg_satisfaction / 5.0) * 40
        
        # 3. Unique student count (0-20 points)
        unique_students = profile.mentor_students_taught
        reach_score = min(20, unique_students)
        
        mentor_score = round(min(100, session_score + satisfaction_score + reach_score), 2)
        
        # Cache
        cache.set(cache_key, mentor_score, ReputationManager.CACHE_TTL)
        return mentor_score
    
    @staticmethod
    def update_all_scores():
        """
        Update all user reputation scores.
        Run via Celery task daily at 2 AM.
        """
        from apps.users.models import UserProfile
        from apps.core.models import RoleProgression
        
        updated = 0
        profiles = UserProfile.objects.all()
        
        for profile in profiles:
            user = profile.user
            old_scores = {
                'creator': profile.creator_score,
                'developer': profile.developer_score,
                'recruiter': profile.recruiter_score,
                'mentor': profile.mentor_score,
            }
            
            # Update all role scores
            if profile.is_creator():
                profile.creator_score = ReputationManager.get_creator_score(user)
            
            if profile.is_developer():
                profile.developer_score = ReputationManager.get_developer_score(user)
            
            if profile.is_recruiter():
                profile.recruiter_score = ReputationManager.get_recruiter_score(user)
            
            if profile.is_mentor():
                profile.mentor_score = ReputationManager.get_mentor_score(user)
            
            profile.save()
            
            # Update progression tiers based on new scores
            roles_to_update = [
                ('creator', 'is_creator'),
                ('developer', 'is_developer'),
                ('recruiter', 'is_recruiter'),
                ('mentor', 'is_mentor'),
            ]
            
            for role_key, is_role_method in roles_to_update:
                if getattr(profile, is_role_method)():
                    score = getattr(profile, f'{role_key}_score')
                    progression, _ = RoleProgression.objects.get_or_create(
                        user=user,
                        role=role_key
                    )
                    progression.update_progress(score)
            
            updated += 1
        
        # Clear all cache keys
        cache_keys = [
            f'{role}_score_{uid}' 
            for role in ['creator', 'developer', 'recruiter', 'mentor']
            for uid in UserProfile.objects.values_list('user_id', flat=True)
        ]
        cache.delete_many(cache_keys)
        
        return f'Updated {updated} user reputation scores'
    
    @staticmethod
    def clear_cache(user_id):
        """
        Clear reputation cache for a specific user.
        Call when user's activity changes (new asset, game review, etc).
        """
        cache_keys = [
            f'creator_score_{user_id}',
            f'developer_score_{user_id}',
            f'recruiter_score_{user_id}',
            f'mentor_score_{user_id}',
        ]
        cache.delete_many(cache_keys)
    
    @staticmethod
    def invalidate_all_cache():
        """
        Clear all reputation scores from cache.
        Useful for testing or manual updates.
        """
        from apps.users.models import UserProfile
        user_ids = UserProfile.objects.values_list('user_id', flat=True)
        for user_id in user_ids:
            ReputationManager.clear_cache(user_id)


def get_trust_badge(score):
    """Convert reputation score to trust badge tier"""
    if score >= 90:
        return {
            'level': 'elite',
            'stars': 5,
            'label': 'Elite',
            'emoji': '⭐⭐⭐⭐⭐',
            'color': '#FFD700',
        }
    elif score >= 75:
        return {
            'level': 'platinum',
            'stars': 4,
            'label': 'Platinum',
            'emoji': '⭐⭐⭐⭐',
            'color': '#E5E4E2',
        }
    elif score >= 50:
        return {
            'level': 'gold',
            'stars': 3,
            'label': 'Gold',
            'emoji': '⭐⭐⭐',
            'color': '#FFD700',
        }
    elif score >= 25:
        return {
            'level': 'silver',
            'stars': 2,
            'label': 'Silver',
            'emoji': '⭐⭐',
            'color': '#C0C0C0',
        }
    else:
        return {
            'level': 'bronze',
            'stars': 1,
            'label': 'Bronze',
            'emoji': '⭐',
            'color': '#CD7F32',
        }
