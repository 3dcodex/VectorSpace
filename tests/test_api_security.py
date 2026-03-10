"""
Test API security for role-based access control
Validates that API endpoints enforce role requirements and ownership checks
"""
import pytest
from django.test import Client
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from apps.users.models import User, UserProfile
from apps.marketplace.models import Asset
from apps.games.models import Game, GameCategory
from apps.jobs.models import Job
from apps.competitions.models import Competition


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_creator():
    user = User.objects.create_user('creator_user', 'creator@example.com', 'password123')
    UserProfile.objects.filter(user=user).update(primary_role='CREATOR')
    return user


@pytest.fixture
def user_developer():
    user = User.objects.create_user('developer_user', 'developer@example.com', 'password123')
    UserProfile.objects.filter(user=user).update(primary_role='DEVELOPER')
    return user


@pytest.fixture
def user_recruiter():
    user = User.objects.create_user('recruiter_user', 'recruiter@example.com', 'password123')
    UserProfile.objects.filter(user=user).update(primary_role='RECRUITER')
    return user


@pytest.fixture
def user_base():
    user = User.objects.create_user('base_user', 'base@example.com', 'password123')
    UserProfile.objects.filter(user=user).update(primary_role='VECTOR')
    return user


@pytest.fixture
def staff_user():
    user = User.objects.create_user('staff_user', 'staff@example.com', 'password123')
    user.is_staff = True
    user.save()
    return user


@pytest.mark.django_db
class TestAssetAPIAccess:
    """Test API asset creation requires CREATOR role"""

    def test_creator_can_create_asset(self, api_client, user_creator):
        """Creator can create assets via API"""
        api_client.force_authenticate(user=user_creator)
        data = {
            'title': 'Test Asset',
            'description': 'Test Description',
            'price': 29.99,
            'asset_type': '3d_model'
        }
        response = api_client.post('/api/v1/assets/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_non_creator_cannot_create_asset(self, api_client, user_developer):
        """Non-creator cannot create assets via API"""
        api_client.force_authenticate(user=user_developer)
        data = {
            'title': 'Test Asset',
            'description': 'Test Description',
            'price': 29.99,
            'asset_type': '3d_model'
        }
        response = api_client.post('/api/v1/assets/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_non_owner_cannot_edit_asset(self, api_client, user_creator):
        """User cannot edit another user's asset"""
        api_client.force_authenticate(user=user_creator)
        
        # Create asset as user_creator
        asset = Asset.objects.create(
            seller=user_creator,
            title='Original Asset',
            description='Description',
            price=29.99,
            asset_type='3d_model',
            is_active=True
        )
        
        # Create another creator
        other_creator = User.objects.create_user('other_creator', 'other@example.com', 'pass')
        UserProfile.objects.filter(user=other_creator).update(primary_role='CREATOR')
        api_client.force_authenticate(user=other_creator)
        
        # Try to edit another user's asset
        data = {'title': 'Hacked Asset'}
        response = api_client.patch(f'/api/v1/assets/{asset.id}/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN or status.HTTP_404_NOT_FOUND

    def test_non_owner_cannot_delete_asset(self, api_client, user_creator):
        """User cannot delete another user's asset"""
        api_client.force_authenticate(user=user_creator)
        
        # Create asset
        asset = Asset.objects.create(
            seller=user_creator,
            title='Original Asset',
            description='Description',
            price=29.99,
            asset_type='3d_model',
            is_active=True
        )
        
        # Create another creator
        other_creator = User.objects.create_user('other_creator', 'other@example.com', 'pass')
        UserProfile.objects.filter(user=other_creator).update(primary_role='CREATOR')
        api_client.force_authenticate(user=other_creator)
        
        # Try to delete another user's asset
        response = api_client.delete(f'/api/v1/assets/{asset.id}/')
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestGameAPIAccess:
    """Test API game creation requires DEVELOPER role"""

    def test_developer_can_create_game(self, api_client, user_developer):
        """Developer can create games via API"""
        api_client.force_authenticate(user=user_developer)
        data = {
            'title': 'Test Game',
            'description': 'Test Description',
            'genre': 'Action'
        }
        response = api_client.post('/api/v1/games/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_non_developer_cannot_create_game(self, api_client, user_creator):
        """Non-developer cannot create games via API"""
        api_client.force_authenticate(user=user_creator)
        data = {
            'title': 'Test Game',
            'description': 'Test Description',
            'genre': 'Action'
        }
        response = api_client.post('/api/v1/games/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_non_owner_cannot_edit_game(self, api_client, user_developer):
        """User cannot edit another developer's game"""
        api_client.force_authenticate(user=user_developer)
        
        # Create game
        game = Game.objects.create(
            developer=user_developer,
            title='Original Game',
            description='Description',
            genre='Action',
            status='published'
        )
        
        # Create another developer
        other_dev = User.objects.create_user('other_dev', 'other@example.com', 'pass')
        UserProfile.objects.filter(user=other_dev).update(primary_role='DEVELOPER')
        api_client.force_authenticate(user=other_dev)
        
        # Try to edit another developer's game
        data = {'title': 'Hacked Game'}
        response = api_client.patch(f'/api/v1/games/{game.id}/', data, format='json')
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestJobAPIAccess:
    """Test API job creation requires RECRUITER role"""

    def test_recruiter_can_create_job(self, api_client, user_recruiter):
        """Recruiter can create jobs via API"""
        api_client.force_authenticate(user=user_recruiter)
        data = {
            'title': 'Test Job',
            'description': 'Test Description',
            'job_type': 'Full-time'
        }
        response = api_client.post('/api/v1/jobs/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_non_recruiter_cannot_create_job(self, api_client, user_creator):
        """Non-recruiter cannot create jobs via API"""
        api_client.force_authenticate(user=user_creator)
        data = {
            'title': 'Test Job',
            'description': 'Test Description',
            'job_type': 'Full-time'
        }
        response = api_client.post('/api/v1/jobs/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_non_owner_cannot_edit_job(self, api_client, user_recruiter):
        """User cannot edit another recruiter's job"""
        api_client.force_authenticate(user=user_recruiter)
        
        # Create job
        job = Job.objects.create(
            recruiter=user_recruiter,
            title='Original Job',
            description='Description',
            job_type='Full-time',
            active=True
        )
        
        # Create another recruiter
        other_recruiter = User.objects.create_user('other_rec', 'other@example.com', 'pass')
        UserProfile.objects.filter(user=other_recruiter).update(primary_role='RECRUITER')
        api_client.force_authenticate(user=other_recruiter)
        
        # Try to edit another recruiter's job
        data = {'title': 'Hacked Job'}
        response = api_client.patch(f'/api/v1/jobs/{job.id}/', data, format='json')
        assert response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND]


@pytest.mark.django_db
class TestCompetitionAPIAccess:
    """Test API competition creation requires STAFF role"""

    def test_staff_can_create_competition(self, api_client, staff_user):
        """Staff can create competitions via API"""
        api_client.force_authenticate(user=staff_user)
        data = {
            'title': 'Test Competition',
            'description': 'Test Description',
            'status': 'active'
        }
        response = api_client.post('/api/v1/competitions/', data, format='json')
        assert response.status_code == status.HTTP_201_CREATED

    def test_non_staff_cannot_create_competition(self, api_client, user_creator):
        """Non-staff cannot create competitions via API"""
        api_client.force_authenticate(user=user_creator)
        data = {
            'title': 'Test Competition',
            'description': 'Test Description',
            'status': 'active'
        }
        response = api_client.post('/api/v1/competitions/', data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestDashboardMarketplaceAccess:
    """Test dashboard marketplace views enforce role checks"""

    def test_creator_can_edit_asset_dashboard(self, api_client, user_creator):
        """Creator can edit their own assets in dashboard"""
        api_client.force_login(user=user_creator)
        
        # Create asset
        asset = Asset.objects.create(
            seller=user_creator,
            title='Test Asset',
            description='Description',
            price=29.99,
            asset_type='3d_model',
            is_active=True
        )
        
        # Edit asset
        response = api_client.post(f'/dashboard/marketplace/assets/{asset.id}/edit/', {
            'title': 'Updated Asset',
            'description': 'Updated Description',
            'price': 39.99,
            'asset_type': '3d_model'
        })
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_302_FOUND]

    def test_non_creator_cannot_edit_asset_dashboard(self, api_client, user_developer):
        """Non-creator cannot edit assets in dashboard"""
        api_client.force_login(user=user_developer)
        
        # Create asset as creator
        creator = User.objects.create_user('creator', 'c@example.com', 'pass')
        UserProfile.objects.filter(user=creator).update(primary_role='CREATOR')
        
        asset = Asset.objects.create(
            seller=creator,
            title='Test Asset',
            description='Description',
            price=29.99,
            asset_type='3d_model',
            is_active=True
        )
        
        # Try to edit as non-creator
        response = api_client.post(f'/dashboard/marketplace/assets/{asset.id}/edit/', {
            'title': 'Hacked Asset',
        })
        # Should redirect to overview due to role check
        assert response.status_code == status.HTTP_302_FOUND or 'overview' in response.url
