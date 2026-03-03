from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('report/', views.report_content, name='report'),
    path('moderation/', views.moderation_dashboard, name='moderation'),
    path('moderation/resolve/<int:report_id>/', views.resolve_report, name='resolve_report'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
]
