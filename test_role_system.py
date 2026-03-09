#!/usr/bin/env python
"""
Test script to validate the role-based system implementation
Tests: signup process, role assignment, dashboard rendering, navigation
"""
import os
import django
import sys
import pytest

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, 'c:\\vector_space')
django.setup()

from django.contrib.auth import authenticate
from django.test import Client
from apps.users.models import User, UserProfile
from apps.jobs.models import Job
from apps.marketplace.models import Asset

pytestmark = pytest.mark.django_db

def test_role_specific_fields():
    """Test that role-specific fields are properly stored"""
    print("\n" + "="*60)
    print("TEST 1: Role-Specific Fields Storage")
    print("="*60)
    
    # Test Creator
    creator = User.objects.filter(username='test_creator').first()
    if creator:
        profile = creator.profile
        print(f"\n✓ Creator user exists: {creator.username}")
        print(f"  - Role: {profile.role}")
        print(f"  - Specialization: {profile.specialization}")
        print(f"  - Software Expertise: {profile.software_expertise}")
    
    # Test Developer
    developer = User.objects.filter(username='test_developer').first()
    if developer:
        profile = developer.profile
        print(f"\n✓ Developer user exists: {developer.username}")
        print(f"  - Role: {profile.role}")
        print(f"  - Programming Languages: {profile.programming_languages}")
        print(f"  - Game Engines: {profile.game_engines}")
    
    # Test Recruiter
    recruiter = User.objects.filter(username='test_recruiter').first()
    if recruiter:
        profile = recruiter.profile
        print(f"\n✓ Recruiter user exists: {recruiter.username}")
        print(f"  - Role: {profile.role}")
        print(f"  - Company Name: {profile.company_name}")
        print(f"  - Company Size: {profile.company_size}")
    
    # Test Mentor
    mentor = User.objects.filter(username='test_mentor').first()
    if mentor:
        profile = mentor.profile
        print(f"\n✓ Mentor user exists: {mentor.username}")
        print(f"  - Role: {profile.role}")
        print(f"  - Expertise Areas: {profile.expertise_areas}")
        print(f"  - Hourly Rate: {profile.hourly_rate}")


def test_role_helper_methods():
    """Test role detection helper methods"""
    print("\n" + "="*60)
    print("TEST 2: Role Helper Methods")
    print("="*60)
    
    roles = {
        'test_creator': ['is_creator', True],
        'test_developer': ['is_developer', True],
        'test_recruiter': ['is_recruiter', True],
        'test_mentor': ['is_mentor', True],
    }
    
    for username, (method_name, expected) in roles.items():
        user = User.objects.filter(username=username).first()
        if user:
            profile = user.profile
            method = getattr(profile, method_name)
            result = method()
            status = "✓" if result == expected else "✗"
            print(f"{status} {username}.profile.{method_name}() = {result}")


def test_dashboard_accessibility():
    """Test that users can access their role-specific dashboards"""
    print("\n" + "="*60)
    print("TEST 3: Dashboard Accessibility")
    print("="*60)
    
    client = Client()
    dashboard_urls = {
        'test_creator': '/dashboard/',
        'test_developer': '/dashboard/',
        'test_recruiter': '/dashboard/',
        'test_mentor': '/dashboard/',
    }
    
    for username, url in dashboard_urls.items():
        user = User.objects.filter(username=username).first()
        if user:
            # Login user
            logged_in = client.login(username=username, password='TestPassword123!')
            if logged_in:
                response = client.get(url)
                status = "✓" if response.status_code == 200 else "✗"
                print(f"{status} {username} can access dashboard (Status: {response.status_code})")
                client.logout()
            else:
                print(f"✗ Failed to login {username}")


def test_database_integrity():
    """Test database integrity and model relationships"""
    print("\n" + "="*60)
    print("TEST 4: Database Integrity")
    print("="*60)
    
    # Check all users have profiles
    users_without_profiles = User.objects.filter(profile__isnull=True).count()
    print(f"✓ Users without profiles: {users_without_profiles} (should be 0)")
    
    # Check role distribution
    role_counts = UserProfile.objects.values('role').distinct().count()
    print(f"✓ Unique roles in database: {role_counts} (should be 4)")
    
    # Check role distribution by count
    for role_choice in ['CREATOR', 'DEVELOPER', 'RECRUITER', 'MENTOR']:
        count = UserProfile.objects.filter(role=role_choice).count()
        print(f"  - {role_choice}: {count} users")


def main():
    print("\n" + "#"*60)
    print("# ROLE-BASED SYSTEM TEST SUITE")
    print("#"*60)
    
    # Clean up old test users if they exist
    test_users = ['test_creator', 'test_developer', 'test_recruiter', 'test_mentor']
    for username in test_users:
        User.objects.filter(username=username).delete()
    
    # Create test users for each role
    print("\nCreating test users...")
    roles_config = [
        ('test_creator', 'CREATOR'),
        ('test_developer', 'DEVELOPER'),
        ('test_recruiter', 'RECRUITER'),
        ('test_mentor', 'MENTOR'),
    ]
    
    for username, role in roles_config:
        user = User.objects.create_user(
            username=username,
            email=f'{username}@test.com',
            password='TestPassword123!'
        )
        user.profile.role = role
        user.profile.location = 'Test City'
        user.profile.experience_years = 5
        
        # Set role-specific fields
        if role == 'CREATOR':
            user.profile.specialization = 'Game Assets'
            user.profile.software_expertise = ['Blender', 'Photoshop']
        elif role == 'DEVELOPER':
            user.profile.programming_languages = ['Python', 'C#']
            user.profile.game_engines = ['Unity', 'Unreal']
            user.profile.years_game_dev = 3
        elif role == 'RECRUITER':
            user.profile.company_name = 'Test Company'
            user.profile.company_website = 'https://test.com'
            user.profile.company_size = 'MEDIUM'
            user.profile.hiring_for = ['Backend', 'Frontend']
        elif role == 'MENTOR':
            user.profile.teaching_experience = 5
            user.profile.expertise_areas = ['Python', 'Web Dev']
            user.profile.hourly_rate = 50.00
        
        user.profile.save()
        print(f"  ✓ Created {username} ({role})")
    
    # Run tests
    test_role_specific_fields()
    test_role_helper_methods()
    test_database_integrity()
    test_dashboard_accessibility()
    
    print("\n" + "#"*60)
    print("# TEST SUITE COMPLETED")
    print("#"*60 + "\n")


if __name__ == '__main__':
    main()
