from django.db import models
from apps.users.models import User

class MentorProfile(models.Model):
    mentor = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    expertise = models.JSONField(default=list)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    total_sessions = models.IntegerField(default=0)
    rating = models.FloatField(default=0)

class MentorshipRequest(models.Model):
    STATUS = [('pending', 'Pending'), ('accepted', 'Accepted'), ('rejected', 'Rejected'), ('completed', 'Completed')]
    mentee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentorship_requests')
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mentorship_offers')
    topic = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

class Session(models.Model):
    request = models.ForeignKey(MentorshipRequest, on_delete=models.CASCADE, related_name='sessions')
    scheduled_at = models.DateTimeField()
    duration_minutes = models.IntegerField()
    notes = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
