from django.urls import path
from . import views_public

app_name = 'jobs'

urlpatterns = [
    # Public URLs - Browse and view jobs
    path('', views_public.job_list, name='list'),
    path('<int:pk>/', views_public.job_detail, name='detail'),
    path('<int:pk>/apply/', views_public.apply_job, name='apply'),
]
