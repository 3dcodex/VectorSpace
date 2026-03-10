from django.db import models
from apps.users.models import User

# Import existing models to keep them

class Report(models.Model):
    REPORT_TYPES = [
        ('spam', 'Spam'),
        ('inappropriate', 'Inappropriate Content'),
        ('harassment', 'Harassment'),
        ('copyright', 'Copyright Violation'),
        ('other', 'Other'),
    ]
    REPORT_STATUS = [
        ('pending', 'Pending'),
        ('reviewing', 'Under Review'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    CONTENT_TYPES = [
        ('post', 'Post'),
        ('comment', 'Comment'),
        ('game', 'Game'),
        ('asset', 'Asset'),
        ('user', 'User'),
    ]
    
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports_made')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    content_id = models.IntegerField()
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='pending')
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_reports')
    moderator_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

class ModerationAction(models.Model):
    ACTION_TYPES = [
        ('warning', 'Warning'),
        ('content_removal', 'Content Removal'),
        ('temporary_ban', 'Temporary Ban'),
        ('permanent_ban', 'Permanent Ban'),
    ]
    
    moderator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='moderation_actions')
    target_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    reason = models.TextField()
    report = models.ForeignKey(Report, on_delete=models.SET_NULL, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Analytics(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    profile_views = models.IntegerField(default=0)
    asset_views = models.IntegerField(default=0)
    asset_downloads = models.IntegerField(default=0)
    game_views = models.IntegerField(default=0)
    game_downloads = models.IntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    class Meta:
        unique_together = ('user', 'date')
        ordering = ['-date']


class ReviewDispute(models.Model):
    """
    Allows users to dispute questionable reviews that hurt their reputation.
    Protects creators from review spam/gaming.
    """
    DISPUTE_REASONS = [
        ('fake_review', 'Fake/Fraudulent Review'),
        ('harassment', 'Harassment/Spam'),
        ('competitor_sabotage', 'Competitor Sabotage'),
        ('inaccurate', 'Factually Inaccurate'),
        ('inappropriate', 'Inappropriate Content'),
        ('other', 'Other'),
    ]
    
    DISPUTE_STATUS = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('upheld', 'Upheld (Review Kept)'),
        ('reversed', 'Reversed (Review Removed)'),
        ('dismissed', 'Dismissed'),
    ]
    
    # Generic review reference (can be asset, game, mentor review)
    review_type = models.CharField(max_length=20, choices=[
        ('asset', 'Asset Review'),
        ('game', 'Game Review'),
        ('mentor', 'Mentor Review'),
    ])
    review_id = models.IntegerField()
    
    # Dispute info
    disputer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='review_disputes')
    reason = models.CharField(max_length=50, choices=DISPUTE_REASONS)
    description = models.TextField()
    evidence_url = models.URLField(blank=True, help_text="Link to evidence")
    
    # Moderation
    status = models.CharField(max_length=20, choices=DISPUTE_STATUS, default='pending')
    moderator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='moderated_disputes')
    moderator_decision = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_review_type_display()} dispute by {self.disputer.username}"


class RoleVerification(models.Model):
    """
    Tracks verification status for professional roles.
    Prevents fake recruiters, scam mentors, etc.
    """
    VERIFICATION_TYPES = [
        ('creator_portfolio', 'Creator Portfolio'),
        ('developer_game', 'Published Game'),
        ('recruiter_company', 'Company Registration'),
        ('recruiter_background', 'Background Check'),
        ('mentor_credentials', 'Teaching Credentials'),
        ('mentor_experience', 'Industry Experience'),
    ]
    
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verifications')
    verification_type = models.CharField(max_length=50, choices=VERIFICATION_TYPES)
    status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    
    # Submission details
    submission_url = models.URLField(blank=True)
    submission_data = models.JSONField(default=dict, blank=True)
    
    # Reviewer info
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='verifications_reviewed')
    reviewer_notes = models.TextField(blank=True)
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('user', 'verification_type')
        ordering = ['-submitted_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_verification_type_display()} ({self.status})"


class RoleProgression(models.Model):
    """
    Tracks user progression through role tiers.
    Novice → Apprentice → Professional → Expert → Elite
    """
    PROGRESSION_TIERS = [
        ('novice', 'Novice', 0),
        ('apprentice', 'Apprentice', 10),
        ('professional', 'Professional', 50),
        ('expert', 'Expert', 85),
        ('elite', 'Elite', 95),
    ]
    
    PROGRESSION_ROLES = [
        ('creator', 'Creator'),
        ('developer', 'Developer'),
        ('recruiter', 'Recruiter'),
        ('mentor', 'Mentor'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='progression')
    role = models.CharField(max_length=20, choices=PROGRESSION_ROLES)
    
    current_tier = models.CharField(max_length=20, default='novice')
    current_score = models.FloatField(default=0)
    
    # Progress toward next tier
    progress_percent = models.IntegerField(default=0)
    next_milestone_score = models.FloatField(default=10)
    
    # Milestones unlocked in this tier
    milestones = models.JSONField(default=list, blank=True)
    
    # Timeline
    tier_achieved_at = models.DateTimeField(auto_now_add=True)
    last_progress_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'role')
        ordering = ['-current_score']
    
    def __str__(self):
        return f"{self.user.username} - {self.role.title()} {self.current_tier.title()}"
    
    def update_progress(self, new_score):
        """Update user's progression in this role"""
        self.current_score = new_score
        
        # Determine tier based on score
        tier_mapping = {
            'novice': (0, 10),
            'apprentice': (10, 50),
            'professional': (50, 85),
            'expert': (85, 95),
            'elite': (95, 100),
        }
        
        for tier_name, (min_score, max_score) in tier_mapping.items():
            if min_score <= new_score < max_score:
                self.current_tier = tier_name
                self.next_milestone_score = max_score
                self.progress_percent = int(((new_score - min_score) / (max_score - min_score)) * 100)
                break
        else:
            # Elite tier
            if new_score >= 95:
                self.current_tier = 'elite'
                self.next_milestone_score = 100
                self.progress_percent = int((new_score - 95) / 5 * 100)
        
        self.save()

