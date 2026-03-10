"""
Test role isolation to ensure each role only sees their own professional tools
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User

# Get admin user
admin = User.objects.filter(is_superuser=True).first()

if not admin:
    print("No admin user found!")
    exit(1)

print(f"Testing role isolation for user: {admin.username}\n")
print("=" * 60)

roles = ['VECTOR', 'CREATOR', 'DEVELOPER', 'RECRUITER', 'MENTOR', None]

for role in roles:
    admin.profile.admin_view_as_role = role
    admin.profile.save()
    admin.profile.refresh_from_db()
    
    role_name = role if role else "MODERATOR (admin_view_as_role=None)"
    print(f"\n▶ Viewing as: {role_name}")
    print("-" * 60)
    print(f"  is_creator: {admin.profile.is_creator()}")
    print(f"  is_developer: {admin.profile.is_developer()}")
    print(f"  is_recruiter: {admin.profile.is_recruiter()}")
    print(f"  is_mentor: {admin.profile.is_mentor()}")
    print(f"  is_moderator: {admin.profile.is_moderator()}")
    print(f"  has_professional_role: {admin.profile.has_professional_role()}")
    
    # Show what navigation sections would be visible
    print(f"\n  Navigation sections visible:")
    
    if admin.profile.is_moderator():
        print("    ✓ Moderator section")
    else:
        print("    ✓ Core section (always visible to non-moderators)")
        
        if admin.profile.has_professional_role():
            print("    ✓ Professional Tools section header")
            if admin.profile.is_creator():
                print("      → Creator tools")
            if admin.profile.is_developer():
                print("      → Developer tools")
            if admin.profile.is_recruiter():
                print("      → Recruiter tools")
            if admin.profile.is_mentor():
                print("      → Mentor tools")
        else:
            print("    ✗ Professional Tools section (no professional role)")
        
        print("    ✓ Collaboration section (always visible)")
        print("    ✓ Personal section (always visible)")
    
print("\n" + "=" * 60)
print("\n✓ Test complete!")
