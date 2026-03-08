"""Public jobs views - browsing job listings"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Job, Application
from .forms import ApplicationForm

def job_list(request):
    """Public: Browse all active job listings"""
    jobs = Job.objects.filter(active=True).order_by('-created_at')
    
    # Filters
    job_type = request.GET.get('type')
    location = request.GET.get('location')
    remote = request.GET.get('remote')
    search = request.GET.get('search')
    
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if remote == 'true':
        jobs = jobs.filter(remote=True)
    if search:
        jobs = jobs.filter(title__icontains=search)
    
    return render(request, 'jobs/public_list.html', {'jobs': jobs})

def job_detail(request, pk):
    """Public: View job details"""
    job = get_object_or_404(Job, pk=pk)
    has_applied = False
    
    if request.user.is_authenticated:
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    
    return render(request, 'jobs/detail.html', {
        'job': job,
        'has_applied': has_applied
    })

@login_required
def apply_job(request, pk):
    """Apply to a job (requires login)"""
    job = get_object_or_404(Job, pk=pk)
    
    # Check if already applied
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.info(request, 'You have already applied to this job.')
        return redirect('jobs:detail', pk=pk)
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()
            
            # Notify recruiter
            send_mail(
                f'New Application for {job.title}',
                f'{request.user.username} has applied for your job posting: {job.title}',
                settings.DEFAULT_FROM_EMAIL,
                [job.recruiter.email],
                fail_silently=True,
            )
            
            messages.success(request, 'Application submitted successfully!')
            return redirect('jobs:detail', pk=pk)
    else:
        form = ApplicationForm()
    
    return render(request, 'jobs/apply.html', {'form': form, 'job': job})
