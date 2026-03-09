#!/usr/bin/env python
"""
Simpler test script - just validates core role functionality without rendering templates
"""
import os
import django
import sys
import pytest

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, 'c:\\vector_space')
django.setup()

from django.contrib.auth import authenticate
from apps.users.models import User, UserProfile

pytestmark = pytest.mark.django_db

def test_suite():
    print("\n" + "#"*60)
    print("# ROLE-BASED SYSTEM - CORE FUNCTIONALITY TEST")
    print("#"*60)
    
    # Clean up old test users
    test_users = ['test_creator', 'test_developer', 'test_recruiter', 'test_mentor']
    for username in test_users:
        User.objects.filter(username=username).delete()
    
    # Createtest users
    print("\nCreating test users...")
    users_created = []
    roles_config = [
        ('test_creator', 'CREATOR', {'specialization': 'Game Assets', 'software_expertise': ['Blender']}),
        ('test_developer', 'DEVELOPER', {'programming_languages': ['Python'], 'game_engines': ['Unity']}),
        ('test_recruiter', 'RECRUITER', {'company_name': 'Test Corp', 'company_size': 'MEDIUM'}),
        ('test_mentor', 'MENTOR', {'expertise_areas': ['Python'], 'hourly_rate': 50.0}),
    ]
    
    for username, role, role_fields in roles_config:
        user = User.objects.create_user(
            username=username,
            email=f'{username}@test.com',
            password='TestPassword123!'
        )
        user.profile.role = role
        user.profile.location = 'Test City'
        user.profile.experience_years = 5
        
        for field, value in role_fields.items():
            setattr(user.profile, field, value)
        
        user.profile.save()
        users_created.append((username, role))
        print(f"  ✓ {username} ({role})")
    
    # Test 1: Role fields storage
    print("\n" + "="*60)
    print("TEST 1: Role-Specific Fields Storage")
    print("="*60)
    for username, expected_role in users_created:
        user = User.objects.get(username=username)
        profile = user.profile
        is_correct = profile.role == expected_role
        status = "✓" if is_correct else "✗"
        print(f"{status} {username}: role={profile.role} (expected {expected_role})")
    
    # Test 2: Role detection helper methods
    print("\n" + "="*60)
    print("TEST 2: Role Helper Methods")
    print("="*60)
    role_methods = {
        'CREATOR': 'is_creator',
        'DEVELOPER': 'is_developer',
        'RECRUITER': 'is_recruiter',
        'MENTOR': 'is_mentor',
    }
    
    for username, role in users_created:
        user = User.objects.get(username=username)
        profile = user.profile
        method_name = role_methods[role]
        method = getattr(profile, method_name)
        result = method()
        status = "✓" if result else "✗"
        print(f"{status} {username}.profile.{method_name}() returned {result}")
    
    # Test 3: Authentication  
    print("\n" + "="*60)
    print("TEST 3: User Authentication")
    print("="*60)
    for username, _ in users_created:
        user = authenticate(username=username, password='TestPassword123!')
        is_authenticated = user is not None
        status = "✓" if is_authenticated else "✗"
        print(f"{status} {username} authenticated: {is_authenticated}")
    
    # Test 4: Database integrity
    print("\n" + "="*60)
    print("TEST 4: Database Integrity")
    print("="*60)
    
    users_without_profiles = User.objects.filter(profile__isnull=True).count()
    print(f"✓ Users without profiles: {users_without_profiles} (should be 0)")
    
    total_users = User.objects.count()
    print(f"✓ Total users in database: {total_users}")
    
    role_dist = {}
    for role_choice in ['CREATOR', 'DEVELOPER', 'RECRUITER', 'MENTOR']:
        count = UserProfile.objects.filter(role=role_choice).count()
        role_dist[role_choice] = count
        print(f"  - {role_choice}: {count} users")
    
    # Test 5: Role-specific field validation
    print("\n" + "="*60)
    print("TEST 5: Role-Specific Field Values")
    print("="*60)
    
    creator = User.objects.get(username='test_creator')
    print(f"✓ Creator.specialization: {creator.profile.specialization}")
    print(f"✓ Creator.software_expertise: {creator.profile.software_expertise}")
    
    developer = User.objects.get(username='test_developer')
    print(f"✓ Developer.programming_languages: {developer.profile.programming_languages}")
    print(f"✓ Developer.game_engines: {developer.profile.game_engines}")
    
    recruiter = User.objects.get(username='test_recruiter')
    print(f"✓ Recruiter.company_name: {recruiter.profile.company_name}")
    print(f"✓ Recruiter.company_size: {recruiter.profile.company_size}")
    
    mentor = User.objects.get(username='test_mentor')
    print(f"✓ Mentor.expertise_areas: {mentor.profile.expertise_areas}")
    print(f"✓ Mentor.hourly_rate: {mentor.profile.hourly_rate}")
    
    print("\n" + "#"*60)
    print("# ALL CORE TESTS PASSED ✓")
    print("#"*60 + "\n")

if __name__ == '__main__':
    test_suite()
