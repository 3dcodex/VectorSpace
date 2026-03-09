from django.urls import path
from . import views_public

app_name = 'jobs'

urlpatterns = [
    # Public URLs - Browse and view jobs
    path('', views_public.job_list, name='list'),
    path('browse/', views_public.job_list, name='browse'),
    path('<int:pk>/', views_public.job_detail, name='detail'),
    path('<int:pk>/apply/', views_public.apply_job, name='apply'),
]
