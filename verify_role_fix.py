"""Quick verification that role isolation fix works"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User

admin = User.objects.filter(is_superuser=True).first()

# Test 1: Moderator mode (admin_view_as_role=None) should not show any roles
admin.profile.admin_view_as_role = None
admin.profile.save()
admin.profile.refresh_from_db()

assert admin.profile.is_moderator() == True, "Should be moderator"
assert admin.profile.is_creator() == False, "Should NOT be creator in moderator mode"
assert admin.profile.is_recruiter() == False, "Should NOT be recruiter in moderator mode"
assert admin.profile.has_professional_role() == False, "Should have NO professional roles in moderator mode"

# Test 2: When viewing as CREATOR, should ONLY be creator
admin.profile.admin_view_as_role = 'CREATOR'
admin.profile.save()
admin.profile.refresh_from_db()

assert admin.profile.is_creator() == True, "Should be creator"
assert admin.profile.is_recruiter() == False, "Should NOT be recruiter when viewing as creator"
assert admin.profile.is_developer() == False, "Should NOT be developer when viewing as creator"

# Test 3: When viewing as VECTOR, should have NO professional roles
admin.profile.admin_view_as_role = 'VECTOR'
admin.profile.save()
admin.profile.refresh_from_db()

assert admin.profile.is_creator() == False, "VECTOR should NOT be creator"
assert admin.profile.is_developer() == False, "VECTOR should NOT be developer"
assert admin.profile.has_professional_role() == False, "VECTOR should have NO professional roles"

print("✅ All role isolation tests PASSED!")
print("✅ Admin role switching now works correctly!")
print("✅ Each role only sees their own professional tools!")
