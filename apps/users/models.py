from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

class User(AbstractUser):
    USER_TYPES = [('gamer', 'Gamer'), ('artist', '3D Artist'), ('developer', 'Developer'), 
                  ('vfx', 'VFX Designer'), ('recruiter', 'Recruiter'), ('mentor', 'Mentor')]
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    bio = models.TextField(blank=True)
    avatar = models.CharField(max_length=255, blank=True)
    portfolio_url = models.URLField(blank=True)
    skills = models.JSONField(default=list)
    rating = models.FloatField(default=0)
    email_verified = models.BooleanField(default=True)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('USER', 'User'),
        ('CREATOR', 'Creator'),
        ('MENTOR', 'Mentor'),
        ('RECRUITER', 'Recruiter'),
        ('ADMIN', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER')
    location = models.CharField(max_length=100, blank=True)
    experience_years = models.IntegerField(default=0)
    verified = models.BooleanField(default=False)
    followers_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    github = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    artstation = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

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
