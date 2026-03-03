from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    
    # Web URLs
    path('users/', include('apps.users.urls')),
    path('marketplace/', include('apps.marketplace.urls')),
    path('jobs/', include('apps.jobs.urls')),
    path('mentorship/', include('apps.mentorship.urls')),
    path('games/', include('apps.games.urls')),
    path('social/', include('apps.social.urls')),
    path('competitions/', include('apps.competitions.urls')),
    path('ai/', include('apps.ai_assistant.urls')),
    path('workspace/', include('apps.workspace.urls')),
    path('core/', include('apps.core.urls')),
    
    # API URLs
    path('api/v1/', include('apps.api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
