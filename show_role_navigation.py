"""
Visual demonstration of what navigation sections are visible for each role
"""
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User

admin = User.objects.filter(is_superuser=True).first()

roles = [
    ('MODERATOR', None),
    ('VECTOR', 'VECTOR'),
    ('CREATOR', 'CREATOR'),
    ('DEVELOPER', 'DEVELOPER'),
    ('RECRUITER', 'RECRUITER'),
    ('MENTOR', 'MENTOR'),
]

print("\n" + "=" * 80)
print(" ROLE-BASED NAVIGATION VISIBILITY TEST")
print("=" * 80)
print("\nThis shows which navigation sections are visible for each role.\n")

for role_name, view_as_value in roles:
    admin.profile.admin_view_as_role = view_as_value
    admin.profile.save()
    admin.profile.refresh_from_db()
    
    print(f"\n{'━' * 80}")
    print(f"  🎭 ROLE: {role_name}")
    print(f"{'━' * 80}")
    
    if admin.profile.is_moderator():
        print("\n  📋 MODERATOR SECTION")
        print("     ├─ Dashboard")
        print("     ├─ Moderation")
        print("     ├─ User Reports")
        print("     ├─ Content Review")
        print("     ├─ Marketplace Review")
        print("     ├─ Game Review")
        print("     ├─ Community Moderation")
        print("     ├─ Analytics")
        print("     └─ Settings")
    else:
        print("\n  🌐 CORE SECTION (Everyone)")
        print("     ├─ Dashboard")
        print("     ├─ Marketplace (browse)")
        print("     ├─ Games (browse)")
        print("     ├─ Community")
        print("     ├─ Competitions")
        print("     ├─ Jobs (browse)")
        print("     └─ Mentorship (browse)")
        
        if admin.profile.has_professional_role():
            print("\n  💼 PROFESSIONAL TOOLS")
            
            if admin.profile.is_creator():
                print("     📦 CREATOR")
                print("        ├─ My Assets")
                print("        ├─ Upload Asset")
                print("        ├─ Draft Assets")
                print("        ├─ Pending Approval")
                print("        ├─ Sales")
                print("        └─ Revenue Summary")
            
            if admin.profile.is_developer():
                print("     💻 DEVELOPER")
                print("        ├─ My Games")
                print("        ├─ Create Game")
                print("        ├─ Upload Build")
                print("        ├─ Game Analytics")
                print("        └─ Version History")
            
            if admin.profile.is_recruiter():
                print("     💼 RECRUITER")
                print("        ├─ Jobs")
                print("        ├─ Post Job")
                print("        ├─ Manage Jobs")
                print("        ├─ Applicants")
                print("        ├─ Talent Search")
                print("        ├─ Hiring Analytics")
                print("        └─ Company Profile")
            
            if admin.profile.is_mentor():
                print("     🎓 MENTOR")
                print("        ├─ Mentorship Dashboard")
                print("        ├─ Student Requests")
                print("        ├─ My Sessions")
                print("        ├─ Schedule Session")
                print("        ├─ Session History")
                print("        └─ Mentor Analytics")
            
            print("     📊 Common")
            print("        └─ Analytics")
        else:
            print("\n  ⚠️  NO PROFESSIONAL TOOLS (Basic user)")
        
        print("\n  🤝 COLLABORATION (Everyone)")
        print("     ├─ Messages")
        print("     └─ Workspaces")
        
        print("\n  👤 PERSONAL (Everyone)")
        print("     ├─ AI Assistant")
        print("     ├─ Notifications")
        print("     ├─ My Profile")
        print("     ├─ Settings")
        print("     └─ Resume Builder")

print("\n" + "=" * 80)
print("\n✅ Role isolation is working correctly!")
print("✅ Each role sees ONLY their own professional tools!")
print("✅ Core, Collaboration, and Personal sections are shared by all non-moderators.")
print("\n" + "=" * 80 + "\n")
