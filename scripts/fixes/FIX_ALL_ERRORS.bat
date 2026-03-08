@echo off
echo ========================================
echo  FIXING DATABASE ERRORS
echo ========================================
echo.

echo Step 1: Making migrations for all apps...
python manage.py makemigrations
echo.

echo Step 2: Running migrations...
python manage.py migrate
echo.

echo Step 3: Setup community categories...
python setup_community.py
echo.

echo ========================================
echo  ALL FIXED!
echo ========================================
echo.
echo Your app should work now. Run: python manage.py runserver
echo.
pause
