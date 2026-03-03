from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import MentorProfile, MentorshipRequest, Session
from .forms import MentorProfileForm, SessionBookingForm, MentorshipRequestForm

def mentor_list(request):
    mentors = MentorProfile.objects.filter(available=True).select_related('mentor')
    
    # Filters
    expertise = request.GET.get('expertise')
    max_rate = request.GET.get('max_rate')
    
    if expertise:
        mentors = mentors.filter(expertise__contains=expertise)
    if max_rate:
        mentors = mentors.filter(hourly_rate__lte=max_rate)
    
    return render(request, 'mentorship/list.html', {'mentors': mentors})

def mentor_detail(request, pk):
    mentor_profile = get_object_or_404(MentorProfile, pk=pk)
    return render(request, 'mentorship/detail.html', {'mentor_profile': mentor_profile})

@login_required
def book_session(request, mentor_id):
    mentor_profile = get_object_or_404(MentorProfile, pk=mentor_id)
    
    if request.method == 'POST':
        request_form = MentorshipRequestForm(request.POST)
        session_form = SessionBookingForm(request.POST)
        
        if request_form.is_valid() and session_form.is_valid():
            # Create mentorship request
            mentorship_request = request_form.save(commit=False)
            mentorship_request.mentee = request.user
            mentorship_request.mentor = mentor_profile.mentor
            mentorship_request.status = 'pending'
            mentorship_request.save()
            
            # Create session
            session = session_form.save(commit=False)
            session.request = mentorship_request
            
            # Check availability (simplified - in production, check against existing sessions)
            scheduled_time = session.scheduled_at
            if scheduled_time < timezone.now():
                messages.error(request, 'Cannot book sessions in the past.')
                return redirect('mentorship:book', mentor_id=mentor_id)
            
            # Calculate cost
            cost = (session.duration_minutes / 60) * mentor_profile.hourly_rate
            
            # In production, process payment here
            # For now, we'll just save the session
            session.save()
            
            # Send confirmation emails
            send_mail(
                'New Mentorship Session Request',
                f'{request.user.username} has requested a session with you.',
                settings.DEFAULT_FROM_EMAIL,
                [mentor_profile.mentor.email],
                fail_silently=True,
            )
            
            send_mail(
                'Session Booking Confirmation',
                f'Your session with {mentor_profile.mentor.username} has been requested. Cost: ${cost:.2f}',
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=True,
            )
            
            messages.success(request, f'Session requested! Cost: ${cost:.2f}. Waiting for mentor confirmation.')
            return redirect('mentorship:my_sessions')
    else:
        request_form = MentorshipRequestForm()
        session_form = SessionBookingForm()
    
    return render(request, 'mentorship/book.html', {
        'mentor_profile': mentor_profile,
        'request_form': request_form,
        'session_form': session_form
    })

@login_required
def my_sessions(request):
    # Sessions as mentee
    mentee_requests = MentorshipRequest.objects.filter(
        mentee=request.user
    ).prefetch_related('sessions').order_by('-created_at')
    
    # Sessions as mentor (if user is a mentor)
    mentor_requests = MentorshipRequest.objects.filter(
        mentor=request.user
    ).prefetch_related('sessions').order_by('-created_at')
    
    return render(request, 'mentorship/my_sessions.html', {
        'mentee_requests': mentee_requests,
        'mentor_requests': mentor_requests
    })

@login_required
def accept_session(request, request_id):
    mentorship_request = get_object_or_404(MentorshipRequest, pk=request_id)
    
    # Only mentor can accept
    if mentorship_request.mentor != request.user:
        messages.error(request, 'You do not have permission to accept this session.')
        return redirect('mentorship:my_sessions')
    
    mentorship_request.status = 'accepted'
    mentorship_request.save()
    
    # Notify mentee
    send_mail(
        'Session Accepted!',
        f'{request.user.username} has accepted your mentorship session request.',
        settings.DEFAULT_FROM_EMAIL,
        [mentorship_request.mentee.email],
        fail_silently=True,
    )
    
    messages.success(request, 'Session accepted!')
    return redirect('mentorship:my_sessions')

@login_required
def reject_session(request, request_id):
    mentorship_request = get_object_or_404(MentorshipRequest, pk=request_id)
    
    # Only mentor can reject
    if mentorship_request.mentor != request.user:
        messages.error(request, 'You do not have permission to reject this session.')
        return redirect('mentorship:my_sessions')
    
    mentorship_request.status = 'rejected'
    mentorship_request.save()
    
    # Notify mentee
    send_mail(
        'Session Request Declined',
        f'{request.user.username} has declined your mentorship session request.',
        settings.DEFAULT_FROM_EMAIL,
        [mentorship_request.mentee.email],
        fail_silently=True,
    )
    
    messages.info(request, 'Session rejected.')
    return redirect('mentorship:my_sessions')

@login_required
def become_mentor(request):
    # Check if already a mentor
    if hasattr(request.user, 'mentor_profile'):
        messages.info(request, 'You are already a mentor.')
        return redirect('mentorship:my_sessions')
    
    if request.method == 'POST':
        form = MentorProfileForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.mentor = request.user
            profile.save()
            
            messages.success(request, 'Mentor profile created! You can now receive session requests.')
            return redirect('mentorship:my_sessions')
    else:
        form = MentorProfileForm()
    
    return render(request, 'mentorship/become_mentor.html', {'form': form})
