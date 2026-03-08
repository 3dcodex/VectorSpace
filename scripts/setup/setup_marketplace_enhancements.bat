@echo off
echo ========================================
echo  Vector Space - Marketplace Enhancement
echo ========================================
echo.

echo Step 1: Creating migrations for Jobs...
python manage.py makemigrations jobs
echo.

echo Step 2: Creating migrations for Marketplace...
python manage.py makemigrations marketplace
echo.

echo Step 3: Creating migrations for Games...
python manage.py makemigrations games
echo.

echo Step 4: Running all migrations...
python manage.py migrate
echo.

echo ========================================
echo  Enhancement Complete!
echo ========================================
echo.
echo New Features Added:
echo.
echo JOBS:
echo  - Experience level filter
echo  - Company name and logo
echo  - Save/bookmark jobs
echo.
echo MARKETPLACE:
echo  - Software compatibility filter
echo  - Poly count display
echo  - Wishlist system
echo.
echo GAMES:
echo  - Platform and engine filters
echo  - Verified badges
echo  - Follow developers
echo  - Trailer support
echo.
echo Visit the pages to see the enhancements:
echo  - Jobs: http://localhost:8000/jobs/
echo  - Marketplace: http://localhost:8000/marketplace/
echo  - Games: http://localhost:8000/games/
echo.
pause
