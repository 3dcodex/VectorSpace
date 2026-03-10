from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class User(AbstractUser):
    bio = models.TextField(blank=True)
    avatar = models.CharField(max_length=255, blank=True)
    portfolio_url = models.URLField(blank=True)
    skills = models.JSONField(default=list)
    rating = models.FloatField(default=0)
    email_verified = models.BooleanField(default=True)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('VECTOR', 'Vector'),  # Primary consumer role in the ecosystem
        ('CREATOR', 'Creator'),  # Provides: assets, templates, sound effects
        ('DEVELOPER', 'Developer'),  # Provides: games, tools, consumes: assets
        ('RECRUITER', 'Recruiter'),  # Provides: jobs, hire talent
        ('MENTOR', 'Mentor'),  # Provides: teaching, mentorship sessions
    ]
    
    # Role progression tiers
    ROLE_TIERS = [
        ('novice', 'Novice'),
        ('apprentice', 'Apprentice'),
        ('professional', 'Professional'),
        ('expert', 'Expert'),
        ('elite', 'Elite'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Multi-role system: Primary role defines main dashboard
    primary_role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='VECTOR')
    
    # Secondary roles: Users can have multiple roles
    # e.g., Developer + Creator, Developer + Mentor
    secondary_roles = models.JSONField(default=list, blank=True, help_text="Additional roles this user performs")

    # Admin-only preview mode to impersonate one role without mutating actual roles.
    admin_view_as_role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    
    # Legacy field for backward compatibility
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='VECTOR')
    
    # Role progression tiers (for gamification)
    creator_tier = models.CharField(max_length=20, choices=ROLE_TIERS, default='novice')
    developer_tier = models.CharField(max_length=20, choices=ROLE_TIERS, default='novice')
    recruiter_tier = models.CharField(max_length=20, choices=ROLE_TIERS, default='novice')
    mentor_tier = models.CharField(max_length=20, choices=ROLE_TIERS, default='novice')
    
    # Role verification status
    creator_verified = models.BooleanField(default=False, help_text="Portfolio verified")
    developer_verified = models.BooleanField(default=False, help_text="Game published + verified")
    recruiter_verified = models.BooleanField(default=False, help_text="Company verified + licensed")
    mentor_verified = models.BooleanField(default=False, help_text="Credentials verified")
    
    # Common fields
    location = models.CharField(max_length=100, blank=True)
    experience_years = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    followers_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    
    # Reputation & Assessment System
    # These track performance across different roles
    creator_score = models.FloatField(default=0, help_text="Asset quality, sales, reviews")
    creator_sales_count = models.IntegerField(default=0)
    creator_total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    developer_score = models.FloatField(default=0, help_text="Game quality, downloads, community engagement")
    developer_games_published = models.IntegerField(default=0)
    developer_total_downloads = models.IntegerField(default=0)
    
    recruiter_score = models.FloatField(default=0, help_text="Hiring success, employer reviews")
    recruiter_successful_hires = models.IntegerField(default=0)
    recruiter_active_jobs = models.IntegerField(default=0)
    
    mentor_score = models.FloatField(default=0, help_text="Teaching quality, student feedback")
    mentor_sessions_completed = models.IntegerField(default=0)
    mentor_students_taught = models.IntegerField(default=0)
    
    # Consumer activity tracking (when acting as USER role)
    assets_purchased = models.IntegerField(default=0)
    games_played = models.IntegerField(default=0)
    jobs_applied = models.IntegerField(default=0)
    mentorship_sessions_taken = models.IntegerField(default=0)
    
    # Social links
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    artstation = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    website = models.URLField(blank=True)
    
    # Creator-specific fields
    specialization = models.CharField(max_length=100, blank=True, help_text="e.g., 3D Artist, VFX Designer, Sound Designer")
    software_expertise = models.JSONField(default=list, blank=True, help_text="Software tools you're proficient in")
    
    # Developer-specific fields
    programming_languages = models.JSONField(default=list, blank=True)
    game_engines = models.JSONField(default=list, blank=True, help_text="Unity, Unreal, Godot, etc.")
    years_game_dev = models.IntegerField(default=0, help_text="Years in game development")
    
    # Recruiter-specific fields
    company_name = models.CharField(max_length=200, blank=True)
    company_website = models.URLField(blank=True)
    company_size = models.CharField(max_length=50, blank=True, help_text="e.g., 1-10, 11-50, 51-200")
    hiring_for = models.JSONField(default=list, blank=True, help_text="Roles actively hiring for")
    
    # Mentor-specific fields
    teaching_experience = models.IntegerField(default=0, help_text="Years of teaching/mentoring")
    expertise_areas = models.JSONField(default=list, blank=True, help_text="Areas of expertise for mentoring")
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    available_for_mentorship = models.BooleanField(default=True)
    
    def __str__(self):
        roles = [self.primary_role] + (self.secondary_roles or [])
        role_str = ' + '.join(roles)
        return f"{self.user.username} - {role_str}"
    
    # Role checker methods - check both primary and secondary roles
    def has_role(self, role_name):
        """Check if user has a specific role (primary or secondary)"""
        def normalize_role(value):
            # Backward compatibility: PLAYER and VECTOR are the same consumer role.
            return 'VECTOR' if value == 'PLAYER' else value

        normalized_role = normalize_role(role_name)

        # Admin impersonation mode: preview one role exactly as that user type.
        if self.user.is_staff or self.user.is_superuser:
            if self.admin_view_as_role:
                # When viewing as a specific role, ONLY that role is active
                return normalized_role == normalize_role(self.admin_view_as_role)
            else:
                # When admin_view_as_role is None, user is in Moderator mode
                # In Moderator mode, don't show any provider role features
                return False

        if normalize_role(self.primary_role) == normalized_role:
            return True
        if self.secondary_roles and normalized_role in [normalize_role(r) for r in self.secondary_roles]:
            return True
        # Backward compatibility for legacy role field
        if normalize_role(self.role) == normalized_role:
            return True
        return False
    
    def is_player(self):
        """Backward-compatible alias for consumer role"""
        return self.is_vector()

    def is_vector(self):
        """Primary consumer role in ecosystem"""
        return self.has_role('VECTOR')

    def is_user(self):
        """Backward-compatible alias for legacy code paths"""
        return self.is_vector()
    
    def is_creator(self):
        """Provides assets, templates, sounds"""
        return self.has_role('CREATOR') or self.role == 'ADMIN'
    
    def is_developer(self):
        """Provides games, tools; consumes assets"""
        return self.has_role('DEVELOPER')
    
    def is_recruiter(self):
        """Provides jobs, hires talent"""
        return self.has_role('RECRUITER')
    
    def is_mentor(self):
        """Provides teaching, mentorship"""
        return self.has_role('MENTOR')
    
    def get_all_roles(self):
        """Returns list of all roles user has"""
        if (self.user.is_staff or self.user.is_superuser) and self.admin_view_as_role:
            return [self.admin_view_as_role]

        roles = [self.primary_role]
        if self.secondary_roles:
            roles.extend(self.secondary_roles)
        return list(set(roles))  # Remove duplicates

    def get_effective_primary_role(self):
        if (self.user.is_staff or self.user.is_superuser) and self.admin_view_as_role:
            return self.admin_view_as_role
        return self.primary_role
    
    def can_provide_service(self, service_type):
        """Check if user can provide a specific service"""
        service_map = {
            'assets': self.is_creator(),
            'games': self.is_developer(),
            'jobs': self.is_recruiter(),
            'mentorship': self.is_mentor(),
        }
        return service_map.get(service_type, False)

    def has_professional_role(self):
        return any([
            self.is_creator(),
            self.is_developer(),
            self.is_recruiter(),
            self.is_mentor(),
        ])

    def is_moderator(self):
        # When impersonating a role, show that role's UX instead of moderator UX.
        return bool((self.user.is_staff or self.user.is_superuser) and not self.admin_view_as_role)

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    profile_visible = models.BooleanField(default=True)
    two_factor_enabled = models.BooleanField(default=False)
    email_job_updates = models.BooleanField(default=True)
    email_marketplace_sales = models.BooleanField(default=True)
    email_competition_announcements = models.BooleanField(default=True)
    email_community_replies = models.BooleanField(default=True)
    notif_direct_messages = models.BooleanField(default=True)
    notif_comments = models.BooleanField(default=True)
    notif_follower_activity = models.BooleanField(default=True)
    public_profile = models.BooleanField(default=True)
    hide_email = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.username} Settings"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        UserSettings.objects.create(user=instance)
