from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('', views.job_list, name='list'),
    path('post/', views.post_job, name='post'),
    path('<int:pk>/', views.job_detail, name='detail'),
    path('<int:pk>/apply/', views.apply_job, name='apply'),
    path('my-applications/', views.my_applications, name='my_applications'),
    path('recruiter/', views.recruiter_dashboard, name='recruiter_dashboard'),
    path('application/<int:pk>/update/', views.update_application_status, name='update_status'),
]
