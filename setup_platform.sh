#!/bin/bash

echo "Setting up Vector Space Platform..."

# Delete old database
if [ -f "db.sqlite3" ]; then
    rm db.sqlite3
    echo "✓ Deleted old database"
fi

# Delete old migrations
find apps/*/migrations -name "*.py" ! -name "__init__.py" -delete
echo "✓ Cleaned old migrations"

# Create media directories
mkdir -p media/assets
mkdir -p media/resumes
mkdir -p media/games
mkdir -p media/submissions
mkdir -p media/posts
mkdir -p media/workspace_files
echo "✓ Created media directories"

# Make migrations
echo "Creating migrations..."
venv/bin/python manage.py makemigrations

# Apply migrations
echo "Applying migrations..."
venv/bin/python manage.py migrate

echo ""
echo "✓ Vector Space Platform setup complete!"
echo ""
echo "Next steps:"
echo "1. (Optional) Create superuser: venv/bin/python manage.py createsuperuser"
echo "2. Run server: venv/bin/python manage.py runserver"
echo "3. Visit: http://localhost:8000/"
echo ""
echo "Platform Features:"
echo "  • 3D Marketplace: /marketplace/"
echo "  • Game Publishing: /games/"
echo "  • Job Board: /jobs/"
echo "  • Mentorship: /mentorship/"
echo "  • Competitions: /competitions/"
echo "  • Community Feed: /social/"
echo "  • AI Assistant: /ai/"
echo "  • Workspaces: /workspace/"
