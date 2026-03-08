"""
Setup script to create default categories for the community
Run this after migrations: python setup_community.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.social.models import Category

def create_categories():
    categories = [
        {'name': 'General', 'slug': 'general', 'icon': '💬'},
        {'name': 'Game Development', 'slug': 'game-dev', 'icon': '🎮'},
        {'name': '3D Modeling', 'slug': '3d-modeling', 'icon': '🎨'},
        {'name': 'Unreal Engine', 'slug': 'unreal-engine', 'icon': '🔷'},
        {'name': 'Unity', 'slug': 'unity', 'icon': '🔶'},
        {'name': 'Job Opportunities', 'slug': 'jobs', 'icon': '💼'},
        {'name': 'Showcases', 'slug': 'showcases', 'icon': '✨'},
        {'name': 'Announcements', 'slug': 'announcements', 'icon': '📢'},
    ]
    
    for cat_data in categories:
        category, created = Category.objects.get_or_create(
            slug=cat_data['slug'],
            defaults={'name': cat_data['name'], 'icon': cat_data['icon']}
        )
        if created:
            print(f"✓ Created category: {category.name}")
        else:
            print(f"- Category already exists: {category.name}")

if __name__ == '__main__':
    print("Setting up community categories...")
    create_categories()
    print("\n✓ Community setup complete!")
