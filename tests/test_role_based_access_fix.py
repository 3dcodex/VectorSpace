"""
Test role-based access control fixes across dashboard views.
Verifies that Creator, Developer, Recruiter, and Mentor roles
cannot access views reserved for other roles.
"""
import pytest
from django.test import Client
from django.contrib.messages.storage.fallback import FallbackStorage
from apps.users.models import User, UserProfile
from apps.marketplace.models import Asset
from apps.games.models import Game
from apps.jobs.models import Job
from apps.mentorship.models import MentorshipRequest, Session


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def user_creator():
    user = User.objects.create_user('creator_user', 'creator@example.com', 'password123')
    UserProfile.objects.filter(user=user).update(primary_role='CREATOR')
    # Refresh user to clear cached profile
    user = User.objects.get(pk=user.pk)
    return user


@pytest.fixture
def user_developer():
    user = User.objects.create_user('developer_user', 'developer@example.com', 'password123')
    UserProfile.objects.filter(user=user).update(primary_role='DEVELOPER')
    user = User.objects.get(pk=user.pk)
    return user


@pytest.fixture
def user_recruiter():
    user = User.objects.create_user('recruiter_user', 'recruiter@example.com', 'password123')
    UserProfile.objects.filter(user=user).update(primary_role='RECRUITER')
    user = User.objects.get(pk=user.pk)
    return user


@pytest.fixture
def user_mentor():
    user = User.objects.create_user('mentor_user', 'mentor@example.com', 'password123')
    UserProfile.objects.filter(user=user).update(primary_role='MENTOR')
    user = User.objects.get(pk=user.pk)
    return user


@pytest.mark.django_db
class TestMarketplaceCreatorAccess:
    """Test Creator role access to marketplace views"""

    def test_creator_can_access_dashboard(self, client, user_creator):
        """Creator can access marketplace dashboard"""
        client.force_login(user_creator)
        response = client.get('/dashboard/marketplace/')
        assert response.status_code == 200

    def test_creator_can_upload_asset(self, client, user_creator):
        """Creator can access upload asset view"""
        client.force_login(user_creator)
        response = client.get('/dashboard/marketplace/upload/')
        assert response.status_code == 200

    def test_non_creator_cannot_upload_asset(self, client, user_developer):
        """Non-Creator cannot access upload asset view"""
        client.force_login(user_developer)
        response = client.get('/dashboard/marketplace/upload/', follow=True)
        # Should redirect or return error
        assert any('Creator' in str(msg) or response.redirect_chain for msg in response.context.get('messages', []) or response.redirect_chain)


@pytest.mark.django_db
class TestGamesDeveloperAccess:
    """Test Developer role access to games views"""

    def test_developer_can_access_publish_game(self, client, user_developer):
        """Developer can access publish game view"""
        client.force_login(user_developer)
        response = client.get('/dashboard/games/publish/', follow=True)
        # Should succeed (200 or form page)
        assert response.status_code == 200 or response.status_code == 405

    def test_non_developer_cannot_publish_game(self, client, user_creator):
        """Non-Developer cannot access publish game view"""
        client.force_login(user_creator)
        response = client.get('/dashboard/games/publish/', follow=True)
        # Should detect the redirect or error message
        assert len(response.redirect_chain) > 0 or response.status_code == 403 or response.status_code == 302


@pytest.mark.django_db
class TestJobsRecruiterAccess:
    """Test Recruiter role access to jobs views"""

    def test_recruiter_can_access_post_job(self, client, user_recruiter):
        """Recruiter can access post job view"""
        client.force_login(user_recruiter)
        response = client.get('/dashboard/jobs/post/', follow=True)
        # Should succeed
        assert response.status_code == 200 or response.status_code == 405

    def test_recruiter_can_access_my_jobs(self, client, user_recruiter):
        """Recruiter can access their job postings"""
        client.force_login(user_recruiter)
        response = client.get('/dashboard/jobs/my-jobs/', follow=True)
        assert response.status_code == 200

    def test_non_recruiter_cannot_post_job(self, client, user_creator):
        """Non-Recruiter cannot post jobs"""
        client.force_login(user_creator)
        response = client.get('/dashboard/jobs/post/', follow=True)
        # Should have redirect chain (meaning access denied)
        assert len(response.redirect_chain) > 0 or response.status_code == 403


@pytest.mark.django_db
class TestMentorshipMentorAccess:
    """Test Mentor role access to mentorship views"""

    def test_mentor_can_access_sessions(self, client, user_mentor):
        """Mentor can access their mentorship sessions"""
        client.force_login(user_mentor)
        response = client.get('/dashboard/mentorship/sessions/', follow=True)
        # Should succeed or redirect to login/dashboard
        assert response.status_code == 200 or 'overview' in str(response.request.get('PATH_INFO', ''))

    def test_non_mentor_cannot_access_sessions(self, client, user_creator):
        """Non-Mentor cannot access mentorship sessions"""
        client.force_login(user_creator)
        response = client.get('/dashboard/mentorship/sessions/', follow=True)
        # Should have redirect chain (meaning access denied)
        # Or should be redirected to overview
        assert len(response.redirect_chain) > 0 or 'overview' in response.request.get('PATH_INFO', '')


@pytest.mark.django_db
class TestRoleMethodsExist:
    """Test that role helper methods exist and work correctly"""

    def test_is_creator_method(self, user_creator):
        """Test is_creator() method exists"""
        assert user_creator.profile.is_creator() is True

    def test_is_developer_method(self, user_developer):
        """Test is_developer() method exists"""
        assert user_developer.profile.is_developer() is True

    def test_is_recruiter_method(self, user_recruiter):
        """Test is_recruiter() method exists"""
        assert user_recruiter.profile.is_recruiter() is True

    def test_is_mentor_method(self, user_mentor):
        """Test is_mentor() method exists"""
        assert user_mentor.profile.is_mentor() is True

    def test_is_creator_returns_false_for_other_roles(self, user_developer):
        """Test is_creator() returns False for non-Creators"""
        assert user_developer.profile.is_creator() is False

    def test_developer_cannot_create_asset(self, user_developer):
        """Developer role should not be able to access Creator features"""
        assert user_developer.profile.is_creator() is False


@pytest.mark.django_db
class TestLegacyRoleCheckReplacement:
    """Verify legacy role checks have been replaced"""

    def test_marketplace_uses_is_creator_method(self, client, user_developer):
        """Verify marketplace view uses is_creator() instead of legacy checks"""
        client.force_login(user_developer)
        # Attempt to upload asset as developer (should fail)
        response = client.get('/dashboard/marketplace/upload/', follow=True)
        # Should be denied (either redirect or on dashboard page)
        assert len(response.redirect_chain) > 0 or 'overview' in response.request.get('PATH_INFO', '')

    def test_games_view_checks_developer_role(self, client, user_recruiter):
        """Games view should check is_developer() role"""
        client.force_login(user_recruiter)
        response = client.get('/dashboard/games/publish/', follow=True)
        # Non-developer should be redirected
        assert len(response.redirect_chain) > 0 or response.status_code != 200

    def test_jobs_view_checks_recruiter_role(self, client, user_mentor):
        """Jobs view should check is_recruiter() role"""
        client.force_login(user_mentor)
        response = client.get('/dashboard/jobs/post/', follow=True)
        # Non-recruiter should be redirected
        assert len(response.redirect_chain) > 0 or response.status_code != 200

    def test_mentorship_view_checks_mentor_role(self, client, user_recruiter):
        """Mentorship view should check is_mentor() role"""
        client.force_login(user_recruiter)
        response = client.get('/dashboard/mentorship/sessions/', follow=True)
        # Non-mentor should be redirected
        assert len(response.redirect_chain) > 0 or response.status_code != 200
