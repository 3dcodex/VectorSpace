import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

print("✅ Django setup successful!")
print(f"✅ Django version: {django.get_version()}")

# Check if templates exist
template_files = [
    'templates/home.html',
    'templates/base.html',
    'static/css/style.css',
    'static/js/main.js'
]

for file in template_files:
    if os.path.exists(file):
        print(f"✅ {file} exists")
    else:
        print(f"❌ {file} missing")

print("\n🚀 Ready to run: python manage.py runserver")
