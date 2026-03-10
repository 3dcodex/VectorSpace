from django.urls import path
from apps.dashboard.views import resume

urlpatterns = [
    path('', resume.build_resume, name='dashboard_resume_builder'),
    path('', resume.build_resume, name='resume_builder'),
    path('save/', resume.save_resume, name='dashboard_resume_save'),
    path('save/', resume.save_resume, name='resume_save'),
    path('preview/', resume.preview_resume, name='dashboard_resume_preview'),
    path('preview/', resume.preview_resume, name='resume_preview'),
]
