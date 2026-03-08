from django.urls import path
from apps.dashboard.views import jobs

urlpatterns = [
    path('', jobs.jobs_board, name='jobs_board'),
    path('<int:pk>/', jobs.dashboard_job_detail, name='jobs_detail'),
    path('<int:pk>/apply/', jobs.dashboard_apply_job, name='jobs_apply'),
    path('applications/', jobs.my_applications, name='jobs_applications'),
    path('post/', jobs.post_job, name='jobs_post'),
    path('postings/', jobs.my_job_postings, name='jobs_postings'),
    path('recruiter/', jobs.recruiter_dashboard, name='jobs_recruiter'),
    path('application/<int:pk>/update/', jobs.update_application_status, name='jobs_update_status'),
]
