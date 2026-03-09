from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.mentorship.models import MentorshipRequest, Session


@login_required
def my_mentorship_sessions(request):
    """List all mentorship sessions for the user"""
    mentor = request.user
    sessions = Session.objects.filter(request__mentor=mentor).select_related('request__mentee')
    return render(request, 'dashboard/mentorship/my_sessions.html', {'sessions': sessions})


@login_required
def manage_sessions(request):
    """Manage mentorship sessions"""
    mentor = request.user
    sessions = Session.objects.filter(request__mentor=mentor).select_related('request__mentee')
    return render(request, 'dashboard/mentorship/manage_sessions.html', {'sessions': sessions})


@login_required
def session_detail(request, pk):
    """View session details"""
    session = get_object_or_404(Session, pk=pk, request__mentor=request.user)
    return render(request, 'dashboard/mentorship/session_detail.html', {'session': session})


@login_required
def complete_session(request, pk):
    """Mark a session as completed"""
    session = get_object_or_404(Session, pk=pk, request__mentor=request.user)
    if request.method == 'POST':
        session.completed = True
        session.save()
        return redirect('dashboard:mentorship_my_sessions')
    return render(request, 'dashboard/mentorship/complete_session.html', {'session': session})


@login_required
def mentorship_requests(request):
    """List all mentorship requests for the mentor"""
    mentor = request.user
    requests = MentorshipRequest.objects.filter(mentor=mentor).select_related('mentee')
    return render(request, 'dashboard/mentorship/requests.html', {'requests': requests})


@login_required
def request_detail(request, pk):
    """View mentorship request details"""
    mentorship_request = get_object_or_404(MentorshipRequest, pk=pk, mentor=request.user)
    return render(request, 'dashboard/mentorship/request_detail.html', {'request': mentorship_request})


@login_required
def respond_to_request(request, pk):
    """Respond to a mentorship request"""
    mentorship_request = get_object_or_404(MentorshipRequest, pk=pk, mentor=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            mentorship_request.status = 'accepted'
            mentorship_request.save()
        elif action == 'reject':
            mentorship_request.status = 'rejected'
            mentorship_request.save()
        return redirect('dashboard:mentorship_requests')
    return render(request, 'dashboard/mentorship/respond_request.html', {'request': mentorship_request})


@login_required
def my_students(request):
    """List all students mentored by this user"""
    mentor = request.user
    mentored_students = MentorshipRequest.objects.filter(
        mentor=mentor,
        status__in=['accepted', 'completed']
    ).values('mentee').distinct()
    
    students = []
    for mentor_req in MentorshipRequest.objects.filter(mentor=mentor, status__in=['accepted', 'completed']):
        if mentor_req.mentee not in [s['mentee'] for s in students]:
            students.append({
                'mentee': mentor_req.mentee,
                'requests_count': MentorshipRequest.objects.filter(mentor=mentor, mentee=mentor_req.mentee).count(),
            })
    
    return render(request, 'dashboard/mentorship/my_students.html', {'students': students})
