from django.urls import path
from apps.dashboard.views import resume

urlpatterns = [
    path('', resume.build_resume, name='resume_builder'),
    path('save/', resume.save_resume, name='resume_save'),
    path('preview/', resume.preview_resume, name='resume_preview'),
]
