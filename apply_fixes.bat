@echo off
echo ========================================
echo Vector Space - Security Fixes Applied
echo ========================================
echo.

REM Activate virtual environment
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo Warning: Virtual environment not found
    echo Please create one with: python -m venv venv
    pause
    exit /b 1
)

echo.
echo Installing required packages...
pip install colorama --quiet

echo.
echo ========================================
echo Running Comprehensive System Tests
echo ========================================
echo.

python test_system_comprehensive.py

echo.
echo ========================================
echo Running Django System Check
echo ========================================
echo.

python manage.py check

echo.
echo ========================================
echo Security Fixes Summary
echo ========================================
echo.
echo [FIXED] SECRET_KEY now loads from environment
echo [FIXED] DEBUG mode controlled by environment
echo [FIXED] ALLOWED_HOSTS restricted
echo [FIXED] Security headers enabled for production
echo [FIXED] Password validation strengthened
echo [FIXED] API rate limiting enabled
echo [FIXED] File upload validation added
echo [FIXED] Email verification bug fixed
echo [FIXED] Input sanitization implemented
echo [FIXED] Query optimization with select_related
echo [FIXED] Logging system enhanced
echo [FIXED] Toast notifications added
echo.
echo ========================================
echo Next Steps
echo ========================================
echo.
echo 1. Update .env file with production values
echo 2. Generate new SECRET_KEY:
echo    python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
echo 3. Run migrations: python manage.py migrate
echo 4. Create superuser: python manage.py createsuperuser
echo 5. Test locally with DEBUG=False
echo 6. Deploy to production
echo.

pause
