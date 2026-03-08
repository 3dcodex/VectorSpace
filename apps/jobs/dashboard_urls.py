from django.urls import path
from . import views

app_name = 'jobs_dashboard'

urlpatterns = [
    path('applications/', views.my_applications, name='my_applications'),
    path('post/', views.post_job, name='post'),
    path('recruiter/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('application/<int:pk>/update/', views.update_application_status, name='update_status'),
]
