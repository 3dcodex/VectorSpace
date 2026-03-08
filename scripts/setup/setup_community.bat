@echo off
echo ========================================
echo  Vector Space - Community Setup
echo ========================================
echo.

echo Step 1: Creating migrations...
python manage.py makemigrations social
echo.

echo Step 2: Running migrations...
python manage.py migrate
echo.

echo Step 3: Setting up categories...
python setup_community.py
echo.

echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo You can now access the community at:
echo http://localhost:8000/social/
echo.
pause
