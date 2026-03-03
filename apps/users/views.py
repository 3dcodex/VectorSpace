from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .forms import UserRegistrationForm
from .models import User, UserProfile

def signup_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            # Profile auto-created by signal, update role
            user.profile.role = form.cleaned_data['role']
            user.profile.save()
            
            # Send verification email
            verification_link = request.build_absolute_uri(
                reverse('users:verify_email', args=[user.verification_token])
            )
            send_mail(
                'Verify Your Email',
                f'Click the link to verify your account: {verification_link}',
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            
            messages.success(request, 'Registration successful! Check your email to verify your account.')
            return redirect('users:login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'users/signup.html', {'form': form})

def verify_email(request, token):
    try:
        user = User.objects.get(verification_token=token)
        user.is_active = True
        user.email_verified = True
        user.save()
        messages.success(request, 'Email verified! You can now log in.')
        return redirect('users:login')
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification link.')
        return redirect('home')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.email_verified:
                login(request, user)
                return redirect('users:dashboard')
            else:
                messages.error(request, 'Please verify your email first.')
        else:
            messages.error(request, 'Invalid credentials.')
    
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')

@login_required
def dashboard_view(request):
    role = request.user.profile.role
    
    if role == 'CREATOR':
        return redirect('users:creator_dashboard')
    elif role == 'MENTOR':
        return redirect('users:mentor_dashboard')
    elif role == 'RECRUITER':
        return redirect('users:recruiter_dashboard')
    elif role == 'ADMIN':
        return redirect('admin:index')
    else:
        return redirect('users:user_dashboard')

@login_required
def user_dashboard(request):
    return render(request, 'users/dashboards/user_dashboard.html')

@login_required
def creator_dashboard(request):
    if request.user.profile.role != 'CREATOR':
        return redirect('users:dashboard')
    
    from apps.marketplace.models import Asset
    from apps.games.models import Game
    
    assets = Asset.objects.filter(seller=request.user)
    games = Game.objects.filter(developer=request.user)
    
    context = {
        'total_assets': assets.count(),
        'total_games': games.count(),
        'total_downloads': sum(a.downloads for a in assets) + sum(g.downloads for g in games),
        'recent_assets': assets.order_by('-created_at')[:5],
        'recent_games': games.order_by('-created_at')[:3],
    }
    return render(request, 'users/dashboards/creator_dashboard.html', context)

@login_required
def mentor_dashboard(request):
    if request.user.profile.role != 'MENTOR':
        return redirect('users:dashboard')
    
    from apps.mentorship.models import MentorProfile, Session
    
    try:
        mentor_profile = MentorProfile.objects.get(mentor=request.user)
        sessions = Session.objects.filter(mentor_profile=mentor_profile)
        context = {
            'mentor_profile': mentor_profile,
            'total_sessions': sessions.count(),
            'upcoming_sessions': sessions.filter(status='scheduled').order_by('scheduled_time')[:5],
        }
    except MentorProfile.DoesNotExist:
        context = {'mentor_profile': None}
    
    return render(request, 'users/dashboards/mentor_dashboard.html', context)

@login_required
def recruiter_dashboard(request):
    if request.user.profile.role != 'RECRUITER':
        return redirect('users:dashboard')
    
    from apps.jobs.models import Job, Application
    
    jobs = Job.objects.filter(recruiter=request.user)
    applications = Application.objects.filter(job__recruiter=request.user)
    
    context = {
        'total_jobs': jobs.count(),
        'active_jobs': jobs.filter(active=True).count(),
        'total_applications': applications.count(),
        'recent_jobs': jobs.order_by('-created_at')[:5],
        'recent_applications': applications.order_by('-applied_at')[:5],
    }
    return render(request, 'users/dashboards/recruiter_dashboard.html', context)
