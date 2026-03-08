@echo off
echo.
echo ========================================
echo Marketplace Dashboard Setup
echo ========================================
echo.

echo Step 1: Making migrations...
python manage.py makemigrations marketplace
echo.

echo Step 2: Running migrations...
python manage.py migrate
echo.

echo Step 3: Testing routes...
python test_marketplace_dashboard.py
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo You can now access the Marketplace Dashboard at:
echo http://localhost:8000/dashboard/marketplace/
echo.
echo Make sure to:
echo 1. Have a user account with CREATOR role
echo 2. Run the development server: python manage.py runserver
echo.
pause
