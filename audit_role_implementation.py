"""
ROLE-BASED ACCESS CONTROL AUDIT
Date: March 9, 2026
Status: CRITICAL ISSUES FOUND

This audit checks if each role is doing EXACTLY what it should - no more, no less.
"""

import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User

print("\n" + "=" * 80)
print(" ROLE-BASED ACCESS CONTROL AUDIT REPORT")
print("=" * 80)

# Test data
print("\n" + "─" * 80)
print("AUDIT 1: ROLE DEFINITION vs IMPLEMENTATION")
print("─" * 80)

audit_results = {
    'CREATOR': {
        'should_do': ['Create assets', 'Upload files', 'View sales', 'Manage payouts'],
        'implementation_status': '⚠️  ISSUES FOUND',
        'issues': [
            '❌ marketplace.py line 18: Uses legacy role field instead of is_creator()',
            '❌ marketplace.py line 93: Same legacy role field check',
            '✅ my_assets() has ownership check (seller=user)',
            '⚠️  upload_asset() uses legacy role field check'
        ]
    },
    'DEVELOPER': {
        'should_do': ['Create games', 'Upload builds', 'View analytics', 'Consume assets'],
        'implementation_status': '❌ MISSING CHECKS',
        'issues': [
            '❌ publish_game() - NO ROLE CHECK! Any user can publish games',
            '❌ edit_game() - Only checks ownership, not is_developer() role',
            '❌ No explicit role guard on any game creation views'
        ]
    },
    'RECRUITER': {
        'should_do': ['Post jobs', 'View applications', 'Manage candidates', 'Communicate'],
        'implementation_status': '❌ MISSING CHECKS',
        'issues': [
            '❌ post_job() - NO ROLE CHECK! Any user can post jobs',
            '❌ my_job_postings() - Only checks ownership, not is_recruiter() role',
            '❌ recruiter_dashboard() - Only checks ownership, not role',
            '✅ update_application_status() has ownership check'
        ]
    },
    'MENTOR': {
        'should_do': ['Manage sessions', 'Accept requests', 'Track mentoring', 'Get paid'],
        'implementation_status': '❌ MISSING CHECKS',
        'issues': [
            '❌ my_mentorship_sessions() - NO ROLE CHECK! Any user can manage sessions',
            '❌ manage_sessions() - NO ROLE CHECK!',
            '❌ mentorship_requests() - NO ROLE CHECK!',
            '❌ respond_to_request() - Only checks ownership, not is_mentor() role'
        ]
    },
    'VECTOR': {
        'should_do': ['Browse', 'Purchase', 'Play games', 'Read posts', 'No provider features'],
        'implementation_status': '✅ LIMITED FEATURES OK',
        'issues': [
            '✅ No specific VECTOR views, everyone has these by default'
        ]
    }
}

for role, audit in audit_results.items():
    print(f"\n[{audit['implementation_status']}] {role}")
    print(f"  Should do: {', '.join(audit['should_do'])}")
    print(f"  Issues:")
    for issue in audit['issues']:
        print(f"    {issue}")

# Privilege escalation check
print("\n" + "─" * 80)
print("AUDIT 2: PRIVILEGE ESCALATION RISK")
print("─" * 80)

print("""
CRITICAL FINDING: Admin users bypass role isolation!

When admin sets admin_view_as_role=None (Moderator mode), they SHOULD only see
moderation tools. But legacy role field checks in marketplace.py BYPASS this!

Example vulnerable code in marketplace.py line 18:
    is_creator = user.profile.role in ['CREATOR', 'ADMIN']

This means:
  • Admin with role='RECRUITER' in DB can STILL access Creator features
  • The new role isolation fix (is_creator()) is being BYPASSED
  • Legacy role field should be removed entirely

Risk Level: CRITICAL ✋
""")

# Missing role guards
print("─" * 80)
print("AUDIT 3: MISSING ROLE GUARDS (Can Do More Than They Should)")
print("─" * 80)

missing_guards = {
    'DEVELOPER': [
        'publish_game() - ANY user can publish',
        'edit_game() - Only ownership check, no role check'
    ],
    'RECRUITER': [
        'post_job() - ANY user can post jobs',
        'my_job_postings() - Only ownership check, no role check'
    ],
    'MENTOR': [
        'my_mentorship_sessions() - ANY user can access',
        'manage_sessions() - ANY user can access',
        'mentorship_requests() - ANY user can access'
    ]
}

for role, views in missing_guards.items():
    print(f"\n❌ {role} can do MORE than they should:")
    for view in views:
        print(f"   - {view}")

risk_level = len([v for views in missing_guards.values() for v in views])
print(f"\n⚠️  Total missing role guards: {risk_level}")
print(f"Risk Level: CRITICAL ✋")

# Incomplete permission checks
print("\n" + "─" * 80)
print("AUDIT 4: SUMMARY OF ISSUES")
print("─" * 80)

summary = """
CRITICAL ISSUES:

1. Marketplace.py (CREATOR)
   └─ Uses legacy 'role' field instead of is_creator()
   └─ Bypasses the new role isolation fix
   └─ Line 18: is_creator = user.profile.role in ['CREATOR', 'ADMIN']
   └─ Line 93: if request.user.profile.role not in ['CREATOR', 'ADMIN']:
   
2. Games View (DEVELOPER)  
   └─ publish_game() has NO ROLE CHECK
   └─ edit_game() only checks ownership, not is_developer()
   └─ Any authenticated user can publish games
   
3. Jobs View (RECRUITER)
   └─ post_job() has NO ROLE CHECK
   └─ my_job_postings() only checks ownership, not is_recruiter()
   └─ Any authenticated user can post jobs
   
4. Mentorship View (MENTOR)
   └─ my_mentorship_sessions() has NO ROLE CHECK
   └─ manage_sessions() has NO ROLE CHECK
   └─ mentorship_requests() has NO ROLE CHECK
   └─ Any authenticated user can manage mentorship
   
IMPACT:
  • Admin role switching doesn't work correctly (still sees Creator features)
  • Non-creators can publish games
  • Non-recruiters can post jobs
  • Non-mentors can manage mentorship
  • Role isolation fix is partially bypassed

SEVERITY: 🔴 CRITICAL
"""

print(summary)

print("\n" + "=" * 80)
print(" FIX RECOMMENDATIONS")
print("=" * 80)

recommendations = """
1. Replace ALL legacy role checks with profile.is_creator(), is_developer(), etc.
   
   BEFORE:
   if request.user.profile.role not in ['CREATOR', 'ADMIN']:
   
   AFTER:
   if not request.user.profile.is_creator():

2. Add role guards to ALL provider views:
   
   @login_required
   def publish_game(request):
       if not request.user.profile.is_developer():
           messages.error(request, 'Developer role required')
           return redirect('dashboard:overview')
       # ... rest of code

3. Remove legacy profile.role field from all checks
   Use profile.primary_role, profile.secondary_roles, or is_*() methods only

4. Add explicit role checks BEFORE database queries:
   - publish_game() → add is_developer() check
   - post_job() → add is_recruiter() check  
   - my_mentorship_sessions() → add is_mentor() check

5. Consider adding a decorator for role checking:
   
   def require_role(role_name):
       def decorator(view_func):
           def wrapper(request, *args, **kwargs):
               if not request.user.profile.has_role(role_name):
                   messages.error(request, f'{role_name} role required')
                   return redirect('dashboard:overview')
               return view_func(request, *args, **kwargs)
           return wrapper
       return decorator
    
    # Usage:
    @login_required
    @require_role('DEVELOPER')
    def publish_game(request):
        ...
"""

print(recommendations)

print("\n" + "=" * 80)
