from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from apps.jobs.models import Job, Application
from apps.jobs.forms import JobPostForm, ApplicationStatusForm, ApplicationForm
from django.db.models import Q


@login_required
def jobs_board(request):
    """Dashboard jobs board (stays inside dashboard)"""
    jobs = Job.objects.filter(active=True).order_by('-created_at')

    job_type = request.GET.get('type')
    location = request.GET.get('location')
    search = request.GET.get('search')
    sort = request.GET.get('sort')

    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if location:
        jobs = jobs.filter(location__icontains=location)
    if search:
        jobs = jobs.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(location__icontains=search)
        )

    if sort in ['-created_at', '-salary_max']:
        jobs = jobs.order_by(sort)

    return render(request, 'jobs/list.html', {'jobs': jobs})


@login_required
def dashboard_job_detail(request, pk):
    """Dashboard-only job detail view"""
    job = get_object_or_404(Job, pk=pk)
    has_applied = Application.objects.filter(job=job, applicant=request.user).exists()
    return render(request, 'jobs/dashboard_detail.html', {
        'job': job,
        'has_applied': has_applied,
    })


@login_required
def dashboard_apply_job(request, pk):
    """Dashboard-only job application flow"""
    job = get_object_or_404(Job, pk=pk)

    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.info(request, 'You have already applied to this job.')
        return redirect('jobs_detail', pk=pk)

    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.applicant = request.user
            application.save()

            send_mail(
                f'New Application for {job.title}',
                f'{request.user.username} has applied for your job posting: {job.title}',
                settings.DEFAULT_FROM_EMAIL,
                [job.recruiter.email],
                fail_silently=True,
            )

            messages.success(request, 'Application submitted successfully!')
            return redirect('jobs_detail', pk=pk)
    else:
        form = ApplicationForm()

    return render(request, 'jobs/dashboard_apply.html', {'form': form, 'job': job})

@login_required
def my_applications(request):
    """List user's job applications"""
    applications = Application.objects.filter(applicant=request.user).order_by('-applied_at')
    return render(request, 'jobs/my_applications.html', {'applications': applications})

@login_required
def post_job(request):
    """Post a new job listing"""
    if request.method == 'POST':
        form = JobPostForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.recruiter = request.user
            job.save()
            
            messages.success(request, f'Job "{job.title}" posted successfully!')
            return redirect('jobs_detail', pk=job.pk)
    else:
        form = JobPostForm()
    
    return render(request, 'jobs/post.html', {'form': form})

@login_required
def my_job_postings(request):
    """List recruiter's job postings"""
    jobs = Job.objects.filter(recruiter=request.user).order_by('-created_at')
    return render(request, 'jobs/my_postings.html', {'jobs': jobs})

@login_required
def recruiter_dashboard(request):
    """Recruiter dashboard with jobs and applications"""
    jobs = Job.objects.filter(recruiter=request.user).order_by('-created_at')
    applications = Application.objects.filter(job__recruiter=request.user).order_by('-applied_at')
    
    return render(request, 'jobs/recruiter_dashboard.html', {
        'jobs': jobs,
        'applications': applications
    })

@login_required
def update_application_status(request, pk):
    """Update application status (recruiter only)"""
    application = get_object_or_404(Application, pk=pk)
    
    # Only recruiter can update status
    if application.job.recruiter != request.user:
        messages.error(request, 'You do not have permission to update this application.')
        return redirect('jobs_recruiter')
    
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
            return redirect('jobs_recruiter')
    
    return redirect('jobs_recruiter')


@login_required
def job_applicants_list(request, job_id):
    """View applicants for a specific job (recruiter only)"""
    job = get_object_or_404(Job, pk=job_id)
    
    #Only recruiter can view
    if job.recruiter != request.user:
        messages.error(request, 'You do not have permission to view these applicants.')
        return redirect('dashboard:jobs_board')
    
    applications = job.applications.all().order_by('-applied_at')
    return render(request, 'dashboard/jobs/applicants_list.html', {
        'job': job,
        'applications': applications
    })


@login_required  
def application_detail(request, pk):
    """View application details (recruiter only)"""
    application = get_object_or_404(Application, pk=pk)
    
    # Only recruiter can view
    if application.job.recruiter != request.user:
        messages.error(request, 'You do not have permission to view this application.')
        return redirect('dashboard:jobs_board')
    
    return render(request, 'dashboard/jobs/application_detail.html', {
        'application': application
    })


