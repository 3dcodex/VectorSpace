import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()


def pick_admin_user():
    user = User.objects.filter(username="admin").first()
    if user:
        return user
    return User.objects.filter(is_superuser=True).order_by("id").first()


def main():
    user = pick_admin_user()
    if not user:
        print("No admin/superuser account found.")
        return

    role = None
    if hasattr(user, "profile"):
        role = user.profile.role

    print("Admin account check")
    print(f"- username: {user.username}")
    print(f"- is_staff: {user.is_staff}")
    print(f"- is_superuser: {user.is_superuser}")
    print(f"- profile.role: {role}")

    client = Client()
    client.force_login(user)

    routes = [
        ("Django admin", "/admin/"),
        ("Dashboard home", "/dashboard/"),
        ("Moderation", "/moderation/"),
        ("Core notifications", "/notifications/"),
        ("Dashboard analytics", "/dashboard/analytics/"),
        ("Dashboard messages", "/dashboard/social/messages/"),
        ("Dashboard marketplace", "/dashboard/marketplace/"),
        ("Dashboard jobs", "/dashboard/jobs/"),
        ("Dashboard mentorship", "/dashboard/mentorship/"),
    ]

    print("\nRoute checks")
    for label, path in routes:
        response = client.get(path)
        print(f"- {label:24} {path:32} status={response.status_code}")

    dashboard = client.get("/dashboard/")
    html = dashboard.content.decode("utf-8", errors="ignore")

    checks = [
        "My Assets",
        "Sales",
        "Messages",
        "Moderation",
        "Post Job",
        "My Sessions",
    ]

    print("\nDashboard nav markers")
    for marker in checks:
        print(f"- contains '{marker}': {marker in html}")


if __name__ == "__main__":
    main()
