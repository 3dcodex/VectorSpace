@echo off
setlocal EnableExtensions DisableDelayedExpansion

set "default_branch=sjeff"

echo ========================================
echo   VECTOR SPACE - SJEFF PUSH SCRIPT
echo ========================================
echo.

REM Ensure git is available.
git --version >nul 2>&1
if errorlevel 1 (
    echo Git is not installed or not in PATH.
    goto :error
)

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

for /f "delims=" %%b in ('git rev-parse --abbrev-ref HEAD 2^>nul') do set "current_branch=%%b"
if "%current_branch%"=="" set "current_branch=%default_branch%"
if /I "%current_branch%"=="HEAD" set "current_branch=%default_branch%"

if /I not "%current_branch%"=="%default_branch%" (
    echo You are currently on branch %current_branch%.
    set /p continue_push=Push this branch instead of %default_branch%? (y/N): 
    if /I not "%continue_push%"=="Y" (
        echo Push aborted. Switch to %default_branch% and run the script again.
        goto :done
    )
)

echo.
echo Adding all files...
git add .
if errorlevel 1 goto :error

REM Warn before committing if deletions are staged.
set "has_deletions="
for /f "delims=" %%d in ('git diff --cached --name-status ^| findstr /B /C:"D"') do set "has_deletions=1"
if defined has_deletions (
    echo.
    echo WARNING: The following deletions are staged:
    git diff --cached --name-status | findstr /B /C:"D"
    echo.
    set /p confirm_delete=Continue with commit and push including deletions? (y/N): 
    if /I not "%confirm_delete%"=="Y" (
        echo Commit aborted by user. Staged changes remain for review.
        goto :done
    )
)

REM If nothing is staged, skip commit/push.
git diff --cached --quiet
if errorlevel 1 goto :has_changes

echo.
echo No staged changes found. Nothing to commit.
goto :done

:has_changes
echo.
set /p commit_msg=Enter commit message (or press Enter for default): 
if "%commit_msg%"=="" set "commit_msg=Update %current_branch% branch"

echo.
echo Creating commit on %current_branch%...
git commit -m "%commit_msg%"
if errorlevel 1 goto :error

REM Ensure the target branch exists locally when HEAD was detached.
git show-ref --verify --quiet refs/heads/%current_branch%
if errorlevel 1 (
    echo.
    echo Creating local branch %current_branch%...
    git checkout -b %current_branch%
    if errorlevel 1 goto :error
)

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