from django.urls import path
from . import views

# No app_name - inherits 'dashboard' namespace from parent include

urlpatterns = [
    path('', views.my_sessions, name='mentorship_my_sessions'),
    path('request/<int:request_id>/accept/', views.accept_session, name='mentorship_accept'),
    path('request/<int:request_id>/reject/', views.reject_session, name='mentorship_reject'),
    path('become-mentor/', views.become_mentor, name='mentorship_become_mentor'),
]
