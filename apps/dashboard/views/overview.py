from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils import timezone
from apps.marketplace.models import Asset, Purchase
from apps.games.models import Game, GameReview
from apps.jobs.models import Application, Job
from apps.mentorship.models import MentorshipRequest

@login_required
def dashboard_overview(request):
    """
    Unified ecosystem dashboard showing provider AND consumer aspects
    Implements the multi-role service flow system
    """
    user = request.user
    profile = user.profile
    
    # Get active role set
    primary_role = profile.get_effective_primary_role()
    secondary_roles = profile.secondary_roles or []
    
    # Map roles to icons and names
    role_map = {
        'VECTOR': {'icon': '🧭', 'name': 'Vector Member'},
        'CREATOR': {'icon': '🎨', 'name': 'Creator'},
        'DEVELOPER': {'icon': '💻', 'name': 'Developer'},
        'RECRUITER': {'icon': '💼', 'name': 'Recruiter'},
        'MENTOR': {'icon': '🎓', 'name': 'Mentor'},
    }
    
    # === PROVIDER STATS (What user offers) ===
    
    # Creator stats
    creator_assets = 0
    creator_sales = 0
    creator_revenue = 0
    creator_score = profile.creator_score
    if profile.is_creator():
        assets = Asset.objects.filter(seller=user)
        creator_assets = assets.count()
        purchases = Purchase.objects.filter(asset__seller=user)
        creator_sales = purchases.count()
        creator_revenue = purchases.aggregate(total=Sum('price_paid'))['total'] or 0
    
    # Developer stats
    developer_games = 0
    developer_downloads = 0
    developer_score = profile.developer_score
    if profile.is_developer():
        games = Game.objects.filter(developer=user)
        developer_games = games.filter(status='published').count()
        developer_downloads = games.aggregate(total=Sum('downloads'))['total'] or 0
    
    # Recruiter stats
    recruiter_jobs = 0
    recruiter_hires = 0
    recruiter_score = profile.recruiter_score
    if profile.is_recruiter():
        jobs = Job.objects.filter(posted_by=user)
        recruiter_jobs = jobs.filter(status='open').count()
        recruiter_hires = profile.recruiter_successful_hires
    
    # Mentor stats
    mentor_sessions = 0
    mentor_students = 0
    mentor_score = profile.mentor_score
    if profile.is_mentor():
        mentor_sessions = profile.mentor_sessions_completed
        mentor_students = profile.mentor_students_taught
    
    # === CONSUMER STATS (What user uses) ===
    
    # Assets purchased
    assets_purchased = Purchase.objects.filter(buyer=user).count()
    assets_spent = Purchase.objects.filter(buyer=user).aggregate(total=Sum('price_paid'))['total'] or 0
    
    # Games played (using game reviews as proxy)
    games_played = GameReview.objects.filter(user=user).count()
    games_reviewed = games_played
    
    # Job applications
    applications = Application.objects.filter(applicant=user)
    jobs_applied = applications.count()
    jobs_pending = applications.filter(status='pending').count()
    
    # Mentorship sessions taken
    mentorship_sessions = MentorshipRequest.objects.filter(mentee=user, status='accepted').count()
    mentors_connected = MentorshipRequest.objects.filter(mentee=user, status='accepted').values('mentor').distinct().count()
    
    # === REPUTATION & TRUST LEVELS ===
    
    def get_trust_stars(score):
        """Convert score to trust level stars (1-5)"""
        if score >= 90: return range(5)
        if score >= 75: return range(4)
        if score >= 50: return range(3)
        if score >= 25: return range(2)
        return range(1)
    
    creator_trust_stars = get_trust_stars(creator_score)
    developer_trust_stars = get_trust_stars(developer_score)
    recruiter_trust_stars = get_trust_stars(recruiter_score)
    mentor_trust_stars = get_trust_stars(mentor_score)
    
    # === USER BADGES ===
    user_badges = user.badges.filter(displayed=True)[:5]  # Top 5 badges
    
    # === RECENT ACTIVITY ===
    recent_activities = []
    
    # Recent purchases
    recent_purchases = Purchase.objects.filter(buyer=user).order_by('-purchased_at')[:3]
    for purchase in recent_purchases:
        recent_activities.append({
            'icon': '🛒',
            'title': f'Purchased "{purchase.asset.title}"',
            'description': f'from {purchase.asset.seller.username}',
            'time_ago': f'{(timezone.now() - purchase.purchased_at).days}d ago'
        })
    
    # Recent sales (if creator)
    if profile.is_creator():
        recent_sales = Purchase.objects.filter(asset__seller=user).order_by('-purchased_at')[:2]
        for sale in recent_sales:
            recent_activities.append({
                'icon': '💰',
                'title': f'Sold "{sale.asset.title}"',
                'description': f'to {sale.buyer.username}',
                'time_ago': f'{(timezone.now() - sale.purchased_at).days}d ago'
            })
    
    # Recent game reviews given
    recent_reviews = GameReview.objects.filter(user=user).order_by('-created_at')[:2]
    for review in recent_reviews:
        recent_activities.append({
            'icon': '⭐',
            'title': f'Reviewed "{review.game.title}"',
            'description': f'{review.rating} stars',
            'time_ago': f'{(timezone.now() - review.created_at).days}d ago'
        })
    
    # Sort by time
    recent_activities = sorted(recent_activities, key=lambda x: x['time_ago'])[:8]
    
    context = {
        'primary_role': primary_role,
        'primary_role_icon': role_map.get(primary_role, {}).get('icon', '🧭'),
        'primary_role_name': role_map.get(primary_role, {}).get('name', 'Vector Member'),
        'secondary_roles': [role_map.get(r, {}) for r in secondary_roles],
        
        # Provider stats
        'creator_assets': creator_assets,
        'creator_sales': creator_sales,
        'creator_revenue': creator_revenue,
        'creator_score': creator_score,
        'creator_trust_stars': creator_trust_stars,
        
        'developer_games': developer_games,
        'developer_downloads': developer_downloads,
        'developer_score': developer_score,
        'developer_trust_stars': developer_trust_stars,
        
        'recruiter_jobs': recruiter_jobs,
        'recruiter_hires': recruiter_hires,
        'recruiter_score': recruiter_score,
        'recruiter_trust_stars': recruiter_trust_stars,
        
        'mentor_sessions': mentor_sessions,
        'mentor_students': mentor_students,
        'mentor_score': mentor_score,
        'mentor_trust_stars': mentor_trust_stars,
        
        # Consumer stats
        'assets_purchased': assets_purchased,
        'assets_spent': assets_spent,
        'games_played': games_played,
        'games_reviewed': games_reviewed,
        'jobs_applied': jobs_applied,
        'jobs_pending': jobs_pending,
        'mentorship_sessions': mentorship_sessions,
        'mentors_connected': mentors_connected,
        
        # Additional
        'user_badges': user_badges,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'dashboard/ecosystem_overview.html', context)
