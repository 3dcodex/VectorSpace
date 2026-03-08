from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import home

urlpatterns = [
    # Public Pages
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    
    # Authentication
    path('auth/', include('apps.users.urls')),
    
    # Public Browse Pages (read-only discovery)
    path('marketplace/', include('apps.marketplace.urls')),
    path('games/', include('apps.games.urls')),
    path('jobs/', include('apps.jobs.urls')),
    path('mentorship/', include('apps.mentorship.urls')),
    path('community/', include('apps.social.urls')),
    path('competitions/', include('apps.competitions.urls')),
    path('', include('apps.core.portfolio_urls')),  # Portfolio URLs (creator/<username>)
    
    # Dashboard (all user-specific actions)
    path('dashboard/', include('apps.dashboard.urls')),
    
    # Core features (reporting, moderation)
    path('', include('apps.core.urls')),
    
    # Workspace and AI
    path('workspace/', include('apps.workspace.urls')),
    path('ai/', include('apps.ai_assistant.urls')),
    
    # API URLs
    path('api/v1/', include('apps.api.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
