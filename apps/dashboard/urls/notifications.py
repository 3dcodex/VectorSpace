from django.urls import path
from apps.dashboard.views import notifications

urlpatterns = [
    path('', notifications.notifications, name='dashboard_notifications'),
    path('', notifications.notifications, name='notifications'),
    path('<int:notification_id>/read/', notifications.mark_notification_read, name='dashboard_notification_read'),
    path('<int:notification_id>/read/', notifications.mark_notification_read, name='notification_read'),
    path('mark-all-read/', notifications.mark_all_read, name='dashboard_notifications_mark_all_read'),
    path('mark-all-read/', notifications.mark_all_read, name='notifications_mark_all_read'),
]
