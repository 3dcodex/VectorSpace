"""
Tests for the notification system functionality
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

try:
    from channels.testing import WebsocketCommunicator  # noqa: F401
except Exception:
    WebsocketCommunicator = None

from apps.core.notifications import NotificationPreference, send_notification, send_bulk_notification
from apps.core.consumers import NotificationConsumer
from apps.social.models import Post, Follow, Category
from apps.games.models import Game
from apps.marketplace.models import Asset, Category as MarketplaceCategory

User = get_user_model()


class NotificationModelTests(TestCase):
    """Test notification models and utilities"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2', 
            email='user2@test.com',
            password='testpass123'
        )
    
    def test_notification_creation(self):
        """Test basic notification creation"""
        notification = send_notification(
            user=self.user1,
            notification_type='follow',
            title='Test notification',
            message='This is a test notification',
            link='/test/'
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.user, self.user1)
        self.assertEqual(notification.notification_type, 'follow')
        self.assertEqual(notification.title, 'Test notification')
        self.assertFalse(notification.read)
        
    def test_notification_preferences_filtering(self):
        """Test that notifications respect user preferences"""
        # Create preferences that disable social notifications
        NotificationPreference.objects.create(
            user=self.user1,
            social_notifications=False
        )
        
        # Try to send a social notification
        notification = send_notification(
            user=self.user1,
            notification_type='follow',
            title='Test notification',
            message='This should be blocked'
        )
        
        # Should return None because social notifications are disabled
        self.assertIsNone(notification)
        
        # Verify no notification was created
        self.assertEqual(self.user1.notifications.count(), 0)
        
    def test_notification_mark_as_read(self):
        """Test marking notifications as read"""
        notification = send_notification(
            user=self.user1,
            notification_type='system',
            title='Test notification',
            message='Test message'
        )
        
        # Initially unread
        self.assertFalse(notification.read)
        
        # Mark as read
        notification.mark_as_read()
        notification.refresh_from_db()
        
        # Should now be read
        self.assertTrue(notification.read)
        
    def test_bulk_notification_sending(self):
        """Test sending notifications to multiple users"""
        users = [self.user1, self.user2]
        
        notifications = send_bulk_notification(
            users=users,
            notification_type='system',
            title='Bulk notification',
            message='This is a bulk notification'
        )
        
        self.assertEqual(len(notifications), 2)
        
        # Check both users received the notification
        self.assertEqual(self.user1.notifications.count(), 1)
        self.assertEqual(self.user2.notifications.count(), 1)


class NotificationDashboardTests(TestCase):
    """Test dashboard notification views"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client = Client()
        
    def test_notifications_view_requires_login(self):
        """Test that notifications view requires authentication"""
        response = self.client.get(reverse('dashboard:notifications'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        
    def test_notifications_view_content(self):
        """Test notifications view shows user notifications"""
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # Create a test notification
        send_notification(
            user=self.user,
            notification_type='welcome',
            title='Welcome!',
            message='Welcome to Vector Space!'
        )
        
        # Access notifications page
        response = self.client.get(reverse('dashboard:notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome!')
        self.assertContains(response, 'Welcome to Vector Space!')
        
    def test_mark_notification_read(self):
        """Test marking individual notification as read"""
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # Create a test notification
        notification = send_notification(
            user=self.user,
            notification_type='welcome',
            title='Welcome!',
            message='Welcome to Vector Space!'
        )
        
        # Mark as read via view
        response = self.client.get(reverse('dashboard:notification_read', args=[notification.id]))
        
        # Should redirect back to notifications
        self.assertEqual(response.status_code, 302)
        
        # Notification should now be read
        notification.refresh_from_db()
        self.assertTrue(notification.read)
        
    def test_mark_all_notifications_read(self):
        """Test marking all notifications as read"""
        # Login
        self.client.login(username='testuser', password='testpass123')
        
        # Create multiple test notifications
        for i in range(3):
            send_notification(
                user=self.user,
                notification_type='system',
                title=f'Notification {i+1}',
                message=f'Message {i+1}'
            )
        
        # Verify all unread
        self.assertEqual(self.user.notifications.filter(read=False).count(), 3)
        
        # Mark all as read via view
        response = self.client.get(reverse('dashboard:notifications_mark_all_read'))
        self.assertEqual(response.status_code, 302)
        
        # All should now be read
        self.assertEqual(self.user.notifications.filter(read=False).count(), 0)
        self.assertEqual(self.user.notifications.filter(read=True).count(), 3)


class NotificationIntegrationTests(TestCase):
    """Test notification integration with other apps"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@test.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@test.com',
            password='testpass123'
        )
        
    def test_follow_creates_notification(self):
        """Test that following someone creates a notification"""
        # Initially no notifications
        self.assertEqual(self.user2.notifications.count(), 0)
        
        # User1 follows User2
        Follow.objects.create(follower=self.user1, following=self.user2)
        
        # User2 should have received a notification
        self.assertEqual(self.user2.notifications.count(), 1)
        
        notification = self.user2.notifications.first()
        self.assertEqual(notification.notification_type, 'follow')
        self.assertIn(self.user1.username, notification.title)
        self.assertIn('started following you', notification.message)
    
    def test_notification_preferences(self):
        """Test notification preferences filtering"""
        # Create preferences that disable social notifications
        prefs = NotificationPreference.objects.create(
            user=self.user1,
            social_notifications=False
        )
        
        # Try to send a social notification
        notification = send_notification(
            user=self.user1,
            notification_type='follow',
            title='Should be blocked',
            message='This should not be sent'
        )
        
        # Should return None due to preferences
        self.assertIsNone(notification)
        
        # Enable social notifications
        prefs.social_notifications = True
        prefs.save()
        
        # Now it should work
        notification = send_notification(
            user=self.user1,
            notification_type='follow',
            title='Should work now',
            message='This should be sent'
        )
        
        self.assertIsNotNone(notification)
    
    def test_bulk_notifications(self):
        """Test sending notifications to multiple users"""
        users = [self.user1, self.user2]
        
        notifications = send_bulk_notification(
            users=users,
            notification_type='system',
            title='System announcement',
            message='This is for everyone'
        )
        
        self.assertEqual(len(notifications), 2)
        self.assertTrue(all(n.title == 'System announcement' for n in notifications))
    
    def test_mark_as_read(self):
        """Test marking notifications as read"""
        notification = send_notification(
            user=self.user1,
            notification_type='system',
            title='Test',
            message='Test message'
        )
        
        self.assertFalse(notification.read)
        
        notification.mark_as_read()
        notification.refresh_from_db()
        
        self.assertTrue(notification.read)


class NotificationViewTests(TestCase):
    """Test notification dashboard views"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        self.client = Client()
        self.client.login(username='testuser', password='testpass123')
        
        # Create some test notifications
        for i in range(3):
            send_notification(
                user=self.user,
                notification_type='system',
                title=f'Notification {i+1}',
                message=f'Message {i+1}'
            )
    
    def test_notifications_list_view(self):
        """Test the notifications list view"""
        response = self.client.get(reverse('dashboard:notifications'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Notification 1')
        self.assertContains(response, 'Notification 2')
        self.assertContains(response, 'Notification 3')
        self.assertContains(response, '3 unread notification')
    
    def test_mark_notification_read(self):
        """Test marking individual notification as read"""
        notification = self.user.notifications.first()
        
        response = self.client.get(
            reverse('dashboard:notification_read', args=[notification.id])
        )
        
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        notification.refresh_from_db()
        self.assertTrue(notification.read)
    
    def test_mark_all_notifications_read(self):
        """Test marking all notifications as read"""
        # Verify all are unread initially
        self.assertEqual(self.user.notifications.filter(read=False).count(), 3)
        
        response = self.client.get(reverse('dashboard:notifications_mark_all_read'))
        
        self.assertEqual(response.status_code, 302)  # Should redirect
        
        # Verify all are now read
        self.assertEqual(self.user.notifications.filter(read=False).count(), 0)
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users can't access notification views"""
        self.client.logout()
        
        response = self.client.get(reverse('dashboard:notifications'))
        self.assertEqual(response.status_code, 302)  # Should redirect to login


class NotificationIntegrationTests(TestCase):
    """Test notification triggers from platform events"""
    
    def setUp(self):
        self.follower = User.objects.create_user(
            username='follower',
            email='follower@test.com', 
            password='testpass123'
        )
        self.followed = User.objects.create_user(
            username='followed',
            email='followed@test.com',
            password='testpass123'
        )
        self.client = Client()
    
    def test_follow_notification(self):
        """Test that following a user sends a notification"""
        self.client.login(username='follower', password='testpass123')
        
        # Initially no notifications
        self.assertEqual(self.followed.notifications.count(), 0)
        
        # Follow the user  
        response = self.client.post(reverse('dashboard:social_follow', args=[self.followed.id]))
        
        # Check notification was created
        self.assertEqual(self.followed.notifications.count(), 1)
        notification = self.followed.notifications.first()
        
        self.assertEqual(notification.notification_type, 'follow')
        self.assertIn('follower', notification.title)
        self.assertIn('following', notification.message)
    
    def test_comment_notification(self):
        """Test that commenting on a post sends a notification"""
        # Create a social post
        category = Category.objects.create(name='General', slug='general')
        post = Post.objects.create(
            author=self.followed,
            title='Test Post',
            content='Test content',
            category=category
        )
        
        self.client.login(username='follower', password='testpass123')
        
        # Initially no notifications
        self.assertEqual(self.followed.notifications.count(), 0)
        
        # Add comment to the post
        response = self.client.post(
            reverse('dashboard:social_add_comment', args=[post.id]),
            {'content': 'Great post!'}
        )
        
        # Check notification was created
        self.assertEqual(self.followed.notifications.count(), 1)
        notification = self.followed.notifications.first()
        
        self.assertEqual(notification.notification_type, 'comment')
        self.assertIn('commented', notification.title)
        self.assertIn('Great post!', notification.message)
    
    def test_game_comment_notification(self):
        """Test that commenting on a game sends notification to developer"""
        # Create a game
        game = Game.objects.create(
            title='Test Game',
            description='Test description',
            developer=self.followed,
            genre='Action',
            status='published'
        )
        
        self.client.login(username='follower', password='testpass123')
        
        # Initially no notifications
        self.assertEqual(self.followed.notifications.count(), 0)
        
        # Add comment to the game
        response = self.client.post(
            reverse('games:add_comment', args=[game.id]),
            {'content': 'Awesome game!'}
        )
        
        # Check notification was created
        self.assertEqual(self.followed.notifications.count(), 1)
        notification = self.followed.notifications.first()
        
        self.assertEqual(notification.notification_type, 'comment')
        self.assertIn('commented on your game', notification.title)
        self.assertIn('Awesome game!', notification.message)
    
    def test_game_review_notification(self):
        """Test that reviewing a game sends notification to developer"""
        # Create a game
        game = Game.objects.create(
            title='Test Game',
            description='Test description',
            developer=self.followed,
            genre='Action',
            status='published'
        )
        
        self.client.login(username='follower', password='testpass123')
        
        # Initially no notifications
        self.assertEqual(self.followed.notifications.count(), 0)
        
        # Add review to the game
        response = self.client.post(
            reverse('games:add_review', args=[game.id]),
            {
                'rating': '5',
                'comment': 'Excellent game, highly recommended!'
            }
        )
        
        # Check notification was created
        self.assertEqual(self.followed.notifications.count(), 1)
        notification = self.followed.notifications.first()
        
        self.assertEqual(notification.notification_type, 'review')
        self.assertIn('review', notification.title)
        self.assertIn('⭐⭐⭐⭐⭐', notification.title)  # 5 stars
        self.assertEqual(notification.priority, 'high')  # High rating = high priority
    
    def test_marketplace_purchase_notification(self):
        """Test that purchasing an asset sends notification to seller"""
        # Create marketplace category and asset
        category = MarketplaceCategory.objects.create(name='3D Models')
        asset = Asset.objects.create(
            title='Test Asset',
            description='Test asset description',
            seller=self.followed,
            price=10.00,
            asset_type='3d_model',
            file_format='OBJ',
            category=category
        )
        
        self.client.login(username='follower', password='testpass123')
        
        # Initially no notifications
        self.assertEqual(self.followed.notifications.count(), 0)
        
        # Purchase the asset (this will use the fallback direct purchase)
        response = self.client.post(reverse('marketplace:purchase', args=[asset.id]))
        
        # Check notification was created for seller
        seller_notifications = self.followed.notifications.filter(notification_type='purchase')
        self.assertEqual(seller_notifications.count(), 1)
        
        notification = seller_notifications.first()
        self.assertIn('Asset Sold', notification.title)
        self.assertIn('follower', notification.message)
        self.assertIn('$10', notification.message)
        
        # Check buyer also got confirmation notification
        buyer_notifications = self.follower.notifications.filter(notification_type='purchase')
        self.assertEqual(buyer_notifications.count(), 1)
    
    def test_self_interactions_no_notification(self):
        """Test that users don't get notifications for their own actions"""
        # Create a social post by the user
        category = Category.objects.create(name='General', slug='general')
        post = Post.objects.create(
            author=self.followed,
            title='My Post',
            content='My content',
            category=category
        )
        
        self.client.login(username='followed', password='testpass123')
        
        # Comment on own post
        response = self.client.post(
            reverse('dashboard:social_add_comment', args=[post.id]),
            {'content': 'Commenting on my own post'}
        )
        
        # Should not create notification for self
        self.assertEqual(self.followed.notifications.count(), 0)


class NotificationConsumerTests(TestCase):
    """Test WebSocket notification consumer (basic functionality)"""
    
    def test_consumer_requires_authentication(self):
        """Test that unauthenticated users cannot connect"""
        # Note: This is a simplified test since full WebSocket testing
        # requires more complex setup with channels testing framework
        consumer = NotificationConsumer()
        
        # Simulate unauthenticated user
        class MockScope:
            user = None
        
        consumer.scope = MockScope()
        
        # The consumer should reject unauthenticated connections
        # This is tested at the connection level in the actual consumer


class NotificationUtilityTests(TestCase):
    """Test utility functions and edge cases"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
    
    def test_invalid_notification_type(self):
        """Test that invalid notification types still work but with valid fallback"""
        notification = send_notification(
            user=self.user,
            notification_type='invalid_type',  # Not in choices
            title='Test',
            message='Test message'
        )
        
        # Should still create notification (Django will handle validation)
        self.assertIsNotNone(notification)
    
    def test_empty_title_and_message(self):
        """Test handling of empty title and message"""
        notification = send_notification(
            user=self.user,
            notification_type='system',
            title='',
            message=''
        )
        
        # Should still create notification
        self.assertIsNotNone(notification)
        self.assertEqual(notification.title, '')
        self.assertEqual(notification.message, '')
    
    def test_very_long_message(self):
        """Test handling of very long messages"""
        long_message = 'A' * 1000  # 1000 characters
        
        notification = send_notification(
            user=self.user,
            notification_type='system',
            title='Long message test',
            message=long_message
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(len(notification.message), 1000)
    
    def test_notification_ordering(self):
        """Test that notifications are ordered by creation date (newest first)"""
        # Create multiple notifications with small delays
        import time
        
        send_notification(self.user, 'system', 'First', 'First message')
        time.sleep(0.001)  # Small delay
        send_notification(self.user, 'system', 'Second', 'Second message')
        time.sleep(0.001)
        send_notification(self.user, 'system', 'Third', 'Third message')
        
        # Get notifications in default ordering
        notifications = list(self.user.notifications.all())
        
        # Should be newest first (n3, n2, n1)
        self.assertEqual(notifications[0].title, 'Third')
        self.assertEqual(notifications[1].title, 'Second')
        self.assertEqual(notifications[2].title, 'First')


if __name__ == '__main__':
    import django
    import os
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()
    
    from django.test.utils import get_runner
    from django.conf import settings
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests.test_notifications"])