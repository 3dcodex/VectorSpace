@echo off
echo ========================================
echo   VECTOR SPACE - GIT PUSH SCRIPT
echo ========================================
echo.

REM Check if git is initialized
if not exist .git (
    echo Initializing git repository...
    git init
    git remote add origin https://github.com/3dcodex/VectorSpace.git
)

echo.
echo Adding all files...
git add .

echo.
echo Creating commit...
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg="Update: Landing page, dashboards, marketplace, and RBAC system"

git commit -m "%commit_msg%"

echo.
echo Pushing to main branch...
git branch -M main
git push -u origin main --force

echo.
echo ========================================
echo   PUSH COMPLETE!
echo ========================================
echo.
pause
