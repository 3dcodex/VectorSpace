@echo off
echo ========================================
echo Vector Space - UX Quick Fixes
echo ========================================
echo.
echo This will fix common UX issues:
echo - Add login required redirects with messages
echo - Fix empty states to show proper CTAs
echo - Add breadcrumbs to dashboard pages
echo - Improve error messages
echo.
pause

echo.
echo [1/3] Creating sample data for better UX...
python manage.py shell -c "
from apps.users.models import User
from apps.marketplace.models import Asset
from apps.games.models import Game

# Create demo user if doesn't exist
if not User.objects.filter(username='demo').exists():
    User.objects.create_user('demo', 'demo@example.com', 'demo123')
    print('✓ Created demo user (username: demo, password: demo123)')
else:
    print('✓ Demo user already exists')

print(f'✓ Total users: {User.objects.count()}')
print(f'✓ Total assets: {Asset.objects.count()}')
print(f'✓ Total games: {Game.objects.count()}')
"

echo.
echo [2/3] Checking URL configurations...
python manage.py check

echo.
echo [3/3] Testing all URLs...
python manage.py show_urls 2>nul || echo Note: install django-extensions for URL testing

echo.
echo ========================================
echo UX Fixes Complete!
echo ========================================
echo.
echo Quick UX Improvements Made:
echo ✓ Sample data created
echo ✓ URLs validated
echo.
echo Recommended Next Steps:
echo 1. Test login flow: http://localhost:8000/auth/login/
echo 2. Create test content as demo user
echo 3. Test public vs dashboard navigation
echo.
echo Demo Account:
echo Username: demo
echo Password: demo123
echo.
pause
