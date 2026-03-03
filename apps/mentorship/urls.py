from django.urls import path
from . import views

app_name = 'mentorship'

urlpatterns = [
    path('', views.mentor_list, name='list'),
    path('mentor/<int:pk>/', views.mentor_detail, name='detail'),
    path('mentor/<int:mentor_id>/book/', views.book_session, name='book'),
    path('my-sessions/', views.my_sessions, name='my_sessions'),
    path('request/<int:request_id>/accept/', views.accept_session, name='accept'),
    path('request/<int:request_id>/reject/', views.reject_session, name='reject'),
    path('become-mentor/', views.become_mentor, name='become_mentor'),
]
