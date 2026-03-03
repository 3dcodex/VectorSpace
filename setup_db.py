import os
import shutil

print("Setting up Vector Space Platform database...")

# Delete old database
if os.path.exists('db.sqlite3'):
    os.remove('db.sqlite3')
    print("✓ Deleted old database")

# Create media directories
media_dirs = [
    'media/assets',
    'media/resumes',
    'media/games',
    'media/submissions',
    'media/posts',
    'media/workspace_files'
]

for dir_path in media_dirs:
    os.makedirs(dir_path, exist_ok=True)

print("✓ Created media directories")
print("\nDatabase reset complete!")
print("\nNext steps:")
print("1. Run: venv/bin/python manage.py makemigrations")
print("2. Run: venv/bin/python manage.py migrate")
print("3. Run: venv/bin/python manage.py runserver")
