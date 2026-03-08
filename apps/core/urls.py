from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Reporting (available to authenticated users)
    path('report/', views.report_content, name='report'),
    
    # Moderation (staff only)
    path('moderation/', views.moderation_dashboard, name='moderation'),
    path('moderation/resolve/<int:report_id>/', views.resolve_report, name='resolve_report'),
    
    # Notification System
    path('notifications/', views.notification_center, name='notifications'),
    path('notifications/preferences/', views.notification_preferences, name='notification_preferences'),
    path('api/notifications/', views.notification_api_list, name='notification_api_list'),
    path('api/notifications/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('api/notifications/delete/', views.delete_notification, name='delete_notification'),
    path('api/notifications/widget/', views.notification_widget, name='notification_widget'),
    
    # Testing endpoint (remove in production)
    path('api/notifications/test/', views.send_test_notification, name='send_test_notification'),
]
