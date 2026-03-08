@echo off
setlocal EnableExtensions DisableDelayedExpansion

echo ========================================
echo   VECTOR SPACE - GIT PUSH SCRIPT
echo ========================================
echo.

REM Initialize git if needed.
if not exist .git (
    echo Initializing git repository...
    git init
    if errorlevel 1 goto :error
)

REM Ensure origin exists.
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo Setting remote origin...
    git remote add origin https://github.com/3dcodex/VectorSpace.git
    if errorlevel 1 goto :error
)

echo.
echo Adding all files...
git add .
if errorlevel 1 goto :error

REM If nothing is staged, skip commit/push.
git diff --cached --quiet
if errorlevel 1 goto :has_changes

echo.
echo No staged changes found. Nothing to commit.
goto :done

:has_changes
echo.
set /p commit_msg=Enter commit message (or press Enter for default): 
if "%commit_msg%"=="" set commit_msg=Update project files

echo.
echo Creating commit...
git commit -m "%commit_msg%"
if errorlevel 1 goto :error

REM Push to the current branch safely (no force push).
for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD 2^>nul') do set current_branch=%%b
if "%current_branch%"=="" set current_branch=main

echo.
echo Pushing to branch %current_branch%...
git push -u origin %current_branch%
if errorlevel 1 goto :error

echo.
echo ========================================
echo   PUSH COMPLETE!
echo ========================================
goto :done

:error
echo.
echo ========================================
echo   PUSH FAILED - CHECK ERRORS ABOVE
echo ========================================

:done
echo.
pause
endlocal
