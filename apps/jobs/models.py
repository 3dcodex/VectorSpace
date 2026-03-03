from django.db import models
from apps.users.models import User

class Job(models.Model):
    JOB_TYPES = [('full_time', 'Full Time'), ('part_time', 'Part Time'), ('contract', 'Contract'), ('freelance', 'Freelance')]
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_postings')
    title = models.CharField(max_length=200)
    description = models.TextField()
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    location = models.CharField(max_length=100)
    remote = models.BooleanField(default=False)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    required_skills = models.JSONField(default=list)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Application(models.Model):
    STATUS = [('pending', 'Pending'), ('reviewed', 'Reviewed'), ('accepted', 'Accepted'), ('rejected', 'Rejected')]
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField()
    resume = models.FileField(upload_to='resumes/')
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
