from django.urls import path
from apps.dashboard.views import mentorship
from apps.mentorship import views as mentorship_public

urlpatterns = [
    path('', mentorship.my_mentorship_sessions, name='mentorship_sessions'),
    path('my-sessions/', mentorship.my_mentorship_sessions, name='mentorship_my_sessions'),
    path('my-sessions/', mentorship.my_mentorship_sessions, name='mentorship_sessions_list'),
    path('requests/', mentorship.mentorship_requests, name='mentorship_requests'),
    path('session/<int:pk>/', mentorship.session_detail, name='mentorship_session_detail'),
    path('session/<int:pk>/', mentorship.session_detail, name='mentorship_session'),
    path('session/<int:pk>/complete/', mentorship.complete_session, name='mentorship_session_complete'),
    path('requests/<int:pk>/', mentorship.request_detail, name='mentorship_request_detail'),
    path('requests/<int:pk>/respond/', mentorship.respond_to_request, name='mentorship_request_respond'),
    path('students/', mentorship.my_students, name='mentorship_students'),
    path('sessions/', mentorship.manage_sessions, name='mentorship_manage_sessions'),

    # Legacy compatibility routes
    path('request/<int:request_id>/accept/', mentorship_public.accept_session, name='mentorship_accept'),
    path('request/<int:request_id>/reject/', mentorship_public.reject_session, name='mentorship_reject'),
    path('become-mentor/', mentorship_public.become_mentor, name='mentorship_become_mentor'),
]
