from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .forms import UserRegistrationForm
from .models import User

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
                return redirect('dashboard:overview')
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
    """Unified dashboard for all users"""
    return render(request, 'users/dashboard.html')

