from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .forms import UserRegistrationForm
from .models import User
import logging

logger = logging.getLogger(__name__)

def signup_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.is_active = False
                user.email_verified = False  # FIX: Set to False initially
                user.save()
                
                # Profile auto-created by signal, update role
                user.profile.primary_role = form.cleaned_data.get('role', 'VECTOR')
                user.profile.save()
                
                # Send verification email
                verification_link = request.build_absolute_uri(
                    reverse('users:verify_email', args=[user.verification_token])
                )
                
                try:
                    send_mail(
                        'Verify Your Email - Vector Space',
                        f'Welcome to Vector Space!\n\n'
                        f'Click the link to verify your account:\n{verification_link}\n\n'
                        f'This link will expire in 24 hours.',
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    logger.info(f'Verification email sent to {user.email}')
                    messages.success(request, 'Registration successful! Check your email to verify your account.')
                except Exception as e:
                    logger.error(f'Email send failed for user {user.id}: {e}', exc_info=True)
                    messages.warning(request, 'Account created but verification email failed. Please contact support.')
                
                return redirect('users:login')
            except Exception as e:
                logger.error(f'Signup failed: {e}', exc_info=True)
                messages.error(request, 'Registration failed. Please try again.')
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
        identifier = (request.POST.get('username') or '').strip()
        password = request.POST.get('password')
        
        try:
            user = authenticate(request, username=identifier, password=password)

            # Fallback: allow login by email address.
            if user is None and identifier:
                lookup_user = User.objects.filter(email__iexact=identifier).first()
                if lookup_user:
                    user = authenticate(request, username=lookup_user.username, password=password)
            
            if user is not None:
                if user.email_verified:
                    login(request, user)
                    logger.info(f'User {user.id} logged in successfully')
                    next_url = request.GET.get('next', 'dashboard:overview')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Please verify your email before logging in.')
            else:
                logger.warning(f'Failed login attempt for identifier: {identifier}')
                messages.error(request, 'Invalid username/email or password. Please try again.')
        except Exception as e:
            logger.error(f'Login error: {e}', exc_info=True)
            messages.error(request, 'Login failed. Please try again.')
    
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully.')
    return redirect('home')

@login_required
def dashboard_view(request):
    """Unified dashboard for all users"""
    return render(request, 'users/dashboard.html')

