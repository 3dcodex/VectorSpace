from django.db import models
from apps.users.models import User

class Competition(models.Model):
    STATUS = [('upcoming', 'Upcoming'), ('active', 'Active'), ('ended', 'Ended')]
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organized_competitions')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50)
    prize_pool = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default='upcoming')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    rules = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Submission(models.Model):
    competition = models.ForeignKey(Competition, on_delete=models.CASCADE, related_name='submissions')
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='competition_submissions')
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='submissions/')
    score = models.FloatField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

class Vote(models.Model):
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('submission', 'voter')
