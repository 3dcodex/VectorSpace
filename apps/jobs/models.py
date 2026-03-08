from django.db import models
from apps.users.models import User

class Job(models.Model):
    JOB_TYPES = [('full_time', 'Full Time'), ('part_time', 'Part Time'), ('contract', 'Contract'), ('freelance', 'Freelance')]
    EXPERIENCE_LEVELS = [('entry', 'Entry Level'), ('mid', 'Mid Level'), ('senior', 'Senior'), ('lead', 'Lead')]
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_postings')
    company_name = models.CharField(max_length=200, default='Company')
    company_logo = models.CharField(max_length=500, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS, default='mid')
    location = models.CharField(max_length=100)
    remote = models.BooleanField(default=False)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    required_skills = models.JSONField(default=list)
    view_count = models.IntegerField(default=0)  # Track page views for recommendations
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now=True)

class Application(models.Model):
    STATUS = [('pending', 'Pending'), ('reviewed', 'Reviewed'), ('accepted', 'Accepted'), ('rejected', 'Rejected')]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)

class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'job')
