from django.urls import path
from . import views

app_name = 'mentorship'

urlpatterns = [
    # Public URLs - Browse mentors
    path('', views.mentor_list, name='list'),
    path('browse/', views.mentor_list, name='browse'),
    path('<int:pk>/', views.mentor_detail, name='detail'),
    path('<int:mentor_id>/book/', views.book_session, name='book'),
    path('become-mentor/', views.become_mentor, name='become_mentor'),
    path('requests/<int:request_id>/accept/', views.accept_session, name='accept'),
    path('requests/<int:request_id>/reject/', views.reject_session, name='reject'),
    
    # Mentor URLs (for dashboard navigation)
    path('profile/edit/', views.edit_mentor_profile, name='profile_edit'),
    path('requests/', views.mentorship_requests, name='requests'),
    path('students/', views.my_students, name='students'),
]
