import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .notifications import Notification

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Accept WebSocket connection and add user to notification group"""
        self.user = self.scope["user"]
        
        # Only allow authenticated users
        if self.user == AnonymousUser():
            await self.close()
            return
        
        # Create a unique group for this user's notifications
        self.notification_group_name = f'notifications_{self.user.id}'
        
        # Join the user's notification group
        await self.channel_layer.group_add(
            self.notification_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send count of unread notifications on connect
        unread_count = await self.get_unread_count()
        await self.send(text_data=json.dumps({
            'type': 'notification_count',
            'count': unread_count
        }))

    async def disconnect(self, close_code):
        """Leave notification group when disconnecting"""
        if hasattr(self, 'notification_group_name'):
            await self.channel_layer.group_discard(
                self.notification_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        """Handle messages from WebSocket (like marking notifications as read)"""
        try:
            text_data_json = json.loads(text_data)
            action = text_data_json.get('action')
            
            if action == 'mark_read':
                notification_id = text_data_json.get('notification_id')
                await self.mark_notification_read(notification_id)
            elif action == 'mark_all_read':
                await self.mark_all_notifications_read()
            elif action == 'get_notifications':
                notifications = await self.get_recent_notifications()
                await self.send(text_data=json.dumps({
                    'type': 'notifications_list',
                    'notifications': notifications
                }))
                
        except json.JSONDecodeError:
            pass

    async def notification_message(self, event):
        """Send notification to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'new_notification',
            'notification': event['notification']
        }))

    async def notification_count_update(self, event):
        """Send updated notification count"""
        await self.send(text_data=json.dumps({
            'type': 'notification_count',
            'count': event['count']
        }))

    @database_sync_to_async
    def get_unread_count(self):
        """Get count of unread notifications for the user"""
        return self.user.notifications.filter(read=False).count()

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark a specific notification as read"""
        try:
            notification = self.user.notifications.get(id=notification_id)
            notification.read = True
            notification.save()
            return True
        except Notification.DoesNotExist:
            return False

    @database_sync_to_async
    def mark_all_notifications_read(self):
        """Mark all notifications as read for the user"""
        self.user.notifications.filter(read=False).update(read=True)

    @database_sync_to_async
    def get_recent_notifications(self, limit=20):
        """Get recent notifications for the user"""
        notifications = self.user.notifications.all()[:limit]
        return [
            {
                'id': notification.id,
                'type': notification.notification_type,
                'title': notification.title,
                'message': notification.message,
                'link': notification.link,
                'read': notification.read,
                'created_at': notification.created_at.isoformat(),
            }
            for notification in notifications
        ]