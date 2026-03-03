import pytest
from django.contrib.auth import get_user_model
from apps.users.models import UserProfile

User = get_user_model()

@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='artist'
        )
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.user_type == 'artist'
        assert user.check_password('testpass123')
    
    def test_user_profile_creation(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='artist'
        )
        profile = UserProfile.objects.create(user=user)
        assert profile.user == user
        assert profile.verified == False

@pytest.mark.django_db
class TestUserViews:
    def test_signup_view(self, client):
        response = client.get('/users/signup/')
        assert response.status_code == 200
    
    def test_login_view(self, client):
        response = client.get('/users/login/')
        assert response.status_code == 200
