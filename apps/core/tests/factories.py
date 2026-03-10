"""
Test data factories for Vector Space.
Use these to quickly generate realistic test data for development and testing.

Example usage:
    user = UserFactory(username='testuser')
    creator = CreatorUserFactory()
    asset = AssetFactory(seller=creator)
    purchase = PurchaseFactory(buyer=developer, asset=asset)
"""

import factory
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.users.models import UserProfile
from apps.marketplace.models import Asset, Category, Purchase, Review as AssetReview
from apps.games.models import Game, GameReview, GameComment
from apps.jobs.models import Job, Application
from apps.mentorship.models import MentorshipRequest, Session

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Create a basic user"""
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user{n}')
    email = factory.LazyAttribute(lambda o: f'{o.username}@example.com')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    is_active = True


class UserProfileFactory(factory.django.DjangoModelFactory):
    """Create a user with profile"""
    class Meta:
        model = UserProfile
    
    user = factory.SubFactory(UserFactory)
    primary_role = 'VECTOR'
    location = factory.Faker('city')
    experience_years = factory.Faker('random_int', min=0, max=20)


class CreatorUserFactory(UserFactory):
    """Create a user with CREATOR role"""
    @factory.post_generation
    def setup_role(obj, create, extracted, **kwargs):
        if not create:
            return
        profile = obj.profile
        profile.primary_role = 'CREATOR'
        profile.verified = True
        profile.creator_verified = True
        # Bootstrap score to avoid cold start
        profile.creator_score = 10
        profile.save()


class DeveloperUserFactory(UserFactory):
    """Create a user with DEVELOPER role"""
    @factory.post_generation
    def setup_role(obj, create, extracted, **kwargs):
        if not create:
            return
        profile = obj.profile
        profile.primary_role = 'DEVELOPER'
        profile.verified = True
        profile.developer_verified = True
        # Bootstrap score
        profile.developer_score = 10
        profile.save()


class RecruiterUserFactory(UserFactory):
    """Create a user with RECRUITER role"""
    @factory.post_generation
    def setup_role(obj, create, extracted, **kwargs):
        if not create:
            return
        profile = obj.profile
        profile.primary_role = 'RECRUITER'
        profile.verified = True
        profile.recruiter_verified = True
        profile.company_name = factory.Faker('company')
        profile.recruiter_score = 10
        profile.save()


class MentorUserFactory(UserFactory):
    """Create a user with MENTOR role"""
    @factory.post_generation
    def setup_role(obj, create, extracted, **kwargs):
        if not create:
            return
        profile = obj.profile
        profile.primary_role = 'MENTOR'
        profile.verified = True
        profile.mentor_verified = True
        profile.teaching_experience = factory.Faker('random_int', min=1, max=20)
        profile.hourly_rate = factory.Faker('pydecimal', left_digits=2, right_digits=2, positive=True)
        profile.mentor_score = 10
        profile.save()


# Marketplace Factories

class CategoryFactory(factory.django.DjangoModelFactory):
    """Create an asset category"""
    class Meta:
        model = Category
    
    name = factory.Faker('word')


class AssetFactory(factory.django.DjangoModelFactory):
    """Create a marketplace asset"""
    class Meta:
        model = Asset
    
    seller = factory.SubFactory(CreatorUserFactory)
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('text', max_nb_chars=200)
    asset_type = factory.Faker('random_element', elements=[
        '3d_model', 'texture', 'plugin', 'script', 'sound', 'vfx', 'material', 'animation'
    ])
    price = factory.Faker('pydecimal', left_digits=3, right_digits=2, positive=True)
    file = factory.django.FileField()
    category = factory.SubFactory(CategoryFactory)
    downloads = factory.Faker('random_int', min=0, max=1000)
    rating = factory.Faker('pydecimal', left_digits=1, right_digits=1, positive=True)
    is_active = True


class PurchaseFactory(factory.django.DjangoModelFactory):
    """Create an asset purchase"""
    class Meta:
        model = Purchase
    
    buyer = factory.SubFactory(DeveloperUserFactory)
    asset = factory.SubFactory(AssetFactory)
    price_paid = factory.LazyAttribute(lambda o: o.asset.price)
    purchased_at = factory.Faker('date_time_this_month', tzinfo=timezone.utc)


class AssetReviewFactory(factory.django.DjangoModelFactory):
    """Create an asset review"""
    class Meta:
        model = AssetReview
    
    user = factory.SubFactory(DeveloperUserFactory)
    asset = factory.SubFactory(AssetFactory)
    rating = factory.Faker('random_int', min=1, max=5)
    comment = factory.Faker('text', max_nb_chars=200)
    created_at = factory.Faker('date_time_this_month', tzinfo=timezone.utc)


# Games Factories

class GameFactory(factory.django.DjangoModelFactory):
    """Create a game"""
    class Meta:
        model = Game
    
    developer = factory.SubFactory(DeveloperUserFactory)
    title = factory.Faker('sentence', nb_words=2)
    description = factory.Faker('text', max_nb_chars=300)
    genre = factory.Faker('random_element', elements=['Action', 'RPG', 'Puzzle', 'Strategy', 'Adventure'])
    platform = factory.Faker('random_element', elements=['pc', 'web', 'mobile', 'console'])
    engine = factory.Faker('random_element', elements=['unity', 'unreal', 'godot', 'custom'])
    status = 'published'
    thumbnail = factory.django.ImageField()
    downloads = factory.Faker('random_int', min=0, max=50000)
    rating = factory.Faker('pydecimal', left_digits=1, right_digits=1, positive=True)
    published_at = factory.Faker('date_time_this_year', tzinfo=timezone.utc)


class GameReviewFactory(factory.django.DjangoModelFactory):
    """Create a game review"""
    class Meta:
        model = GameReview
    
    game = factory.SubFactory(GameFactory)
    user = factory.SubFactory(UserFactory)
    rating = factory.Faker('random_int', min=1, max=5)
    comment = factory.Faker('text', max_nb_chars=200)
    created_at = factory.Faker('date_time_this_month', tzinfo=timezone.utc)


class GameCommentFactory(factory.django.DjangoModelFactory):
    """Create a game comment"""
    class Meta:
        model = GameComment
    
    game = factory.SubFactory(GameFactory)
    user = factory.SubFactory(UserFactory)
    content = factory.Faker('text', max_nb_chars=150)
    created_at = factory.Faker('date_time_this_month', tzinfo=timezone.utc)


# Jobs Factories

class JobFactory(factory.django.DjangoModelFactory):
    """Create a job posting"""
    class Meta:
        model = Job
    
    recruiter = factory.SubFactory(RecruiterUserFactory)
    company_name = factory.LazyAttribute(lambda o: o.recruiter.profile.company_name or factory.Faker('company'))
    title = factory.Faker('job')
    description = factory.Faker('text', max_nb_chars=300)
    job_type = factory.Faker('random_element', elements=['full_time', 'part_time', 'contract', 'freelance'])
    experience_level = factory.Faker('random_element', elements=['entry', 'mid', 'senior', 'lead'])
    location = factory.Faker('city')
    remote = factory.Faker('boolean')
    salary_min = factory.Faker('pydecimal', left_digits=5, right_digits=2, positive=True)
    salary_max = factory.LazyAttribute(lambda o: o.salary_min * 1.2)
    required_skills = factory.Faker('words', nb=5)
    active = True


class ApplicationFactory(factory.django.DjangoModelFactory):
    """Create a job application"""
    class Meta:
        model = Application
    
    job = factory.SubFactory(JobFactory)
    applicant = factory.SubFactory(DeveloperUserFactory)
    cover_letter = factory.Faker('text', max_nb_chars=300)
    resume = factory.django.FileField()
    status = 'pending'
    applied_at = factory.Faker('date_time_this_month', tzinfo=timezone.utc)


# Mentorship Factories

class MentorshipRequestFactory(factory.django.DjangoModelFactory):
    """Create a mentorship request"""
    class Meta:
        model = MentorshipRequest
    
    mentee = factory.SubFactory(UserFactory)
    mentor = factory.SubFactory(MentorUserFactory)
    topic = factory.Faker('sentence', nb_words=3)
    description = factory.Faker('text', max_nb_chars=200)
    status = 'accepted'
    created_at = factory.Faker('date_time_this_month', tzinfo=timezone.utc)


class SessionFactory(factory.django.DjangoModelFactory):
    """Create a mentorship session"""
    class Meta:
        model = Session
    
    request = factory.SubFactory(MentorshipRequestFactory)
    scheduled_at = factory.Faker('date_time_this_month', tzinfo=timezone.utc)
    duration_minutes = factory.Faker('random_int', min=30, max=120)
    completed = True


# Batch Factories

class FullEcosystemFactory:
    """
    Create a complete ecosystem with multiple user types and interactions.
    Useful for testing reputation calculations and ecosystem health.
    """
    
    @staticmethod
    def create_ecosystem(num_creators=5, num_developers=10, num_recruiters=3, num_mentors=5):
        """
        Create a realistic ecosystem:
        - N creators with assets
        - N developers buying assets and publishing games
        - N recruiters posting jobs
        - N mentors offering mentorship
        - Cross-role interactions
        """
        
        # Create users
        creators = [CreatorUserFactory() for _ in range(num_creators)]
        developers = [DeveloperUserFactory() for _ in range(num_developers)]
        recruiters = [RecruiterUserFactory() for _ in range(num_recruiters)]
        mentors = [MentorUserFactory() for _ in range(num_mentors)]
        
        # Creators publish assets
        assets = []
        for creator in creators:
            for _ in range(3):  # 3 assets per creator
                assets.append(AssetFactory(seller=creator))
        
        # Developers buy assets
        for developer in developers:
            for asset in assets[::2]:  # Every other asset
                PurchaseFactory(buyer=developer, asset=asset)
                # Add reviews
                AssetReviewFactory(user=developer, asset=asset)
        
        # Developers publish games
        games = []
        for developer in developers:
            for _ in range(2):  # 2 games per developer
                games.append(GameFactory(developer=developer))
        
        # Players (other developers + regular users) review games
        all_users = creators + developers + recruiters + mentors
        for game in games:
            for user in all_users[::3]:  # Every 3rd user
                GameReviewFactory(game=game, user=user)
        
        # Recruiters post jobs
        jobs = []
        for recruiter in recruiters:
            for _ in range(3):  # 3 jobs per recruiter
                jobs.append(JobFactory(recruiter=recruiter))
        
        # Developers apply for jobs
        for job in jobs:
            for developer in developers[::2]:  # Every other developer
                ApplicationFactory(job=job, applicant=developer)
        
        # Mentors offer mentorship to developers
        for mentor in mentors:
            for developer in developers[::3]:
                req = MentorshipRequestFactory(mentee=developer, mentor=mentor)
                # Create completed sessions
                for _ in range(2):
                    SessionFactory(request=req)
        
        return {
            'creators': creators,
            'developers': developers,
            'recruiters': recruiters,
            'mentors': mentors,
            'assets': assets,
            'games': games,
            'jobs': jobs,
        }
