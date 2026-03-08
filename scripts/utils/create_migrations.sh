#!/bin/bash

# Create migrations for all new models
echo "Creating migrations for all apps..."

python manage.py makemigrations users
python manage.py makemigrations marketplace
python manage.py makemigrations games
python manage.py makemigrations social
python manage.py makemigrations jobs
python manage.py makemigrations mentorship
python manage.py makemigrations competitions
python manage.py makemigrations workspace
python manage.py makemigrations ai_assistant
python manage.py makemigrations core

echo "Migrations created successfully!"
echo ""
echo "To apply migrations, run:"
echo "python manage.py migrate"
