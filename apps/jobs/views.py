from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Job, Application
from .forms import JobPostForm, ApplicationForm, ApplicationStatusForm

def job_list(request):
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
    
    return render(request, 'jobs/list.html', {'jobs': jobs})

def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    has_applied = False
    
    if request.user.is_authenticated:
        has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    
    return render(request, 'jobs/detail.html', {
        'job': job,
        'has_applied': has_applied
    })

@login_required
def post_job(request):
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            
            messages.success(request, f'Job "{job.title}" posted successfully!')
            return redirect('jobs:detail', pk=job.pk)
    else:
        form = JobPostForm()
    
    return render(request, 'jobs/post.html', {'form': form})

@login_required
def apply_job(request, pk):
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

@login_required
def my_applications(request):
    applications = Application.objects.filter(applicant=request.user).order_by('-applied_at')
    return render(request, 'jobs/my_applications.html', {'applications': applications})

@login_required
def recruiter_dashboard(request):
    jobs = Job.objects.filter(recruiter=request.user).order_by('-created_at')
    applications = Application.objects.filter(job__recruiter=request.user).order_by('-applied_at')
    
    return render(request, 'jobs/recruiter_dashboard.html', {
        'jobs': jobs,
        'applications': applications
    })

@login_required
def update_application_status(request, pk):
    application = get_object_or_404(Application, pk=pk)
    
    # Only recruiter can update status
    if application.job.recruiter != request.user:
        messages.error(request, 'You do not have permission to update this application.')
        return redirect('jobs:recruiter_dashboard')
    
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            
            # Notify applicant
            send_mail(
                f'Application Status Update: {application.job.title}',
                f'Your application status has been updated to: {application.get_status_display()}',
                settings.DEFAULT_FROM_EMAIL,
                [application.applicant.email],
                fail_silently=True,
            )
            
            messages.success(request, 'Application status updated!')
            return redirect('jobs:recruiter_dashboard')
    
    return redirect('jobs:recruiter_dashboard')
