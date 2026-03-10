@echo off
setlocal EnableExtensions DisableDelayedExpansion

set "default_branch=B"

echo ========================================
echo   VECTOR SPACE - B PUSH SCRIPT
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

REM If there are staged changes, commit them before syncing with the remote branch.
git diff --cached --quiet
if errorlevel 1 goto :has_changes

echo.
echo No staged changes found. Skipping commit.
goto :sync_branch

:has_changes
echo.
set /p commit_msg=Enter commit message (or press Enter for default): 
if "%commit_msg%"=="" set "commit_msg=Update %current_branch% branch"

echo.
echo Creating commit on %current_branch%...
git commit -m "%commit_msg%"
if errorlevel 1 goto :error

:sync_branch
echo.
echo Fetching latest remote state...
git fetch origin
if errorlevel 1 goto :error

git ls-remote --exit-code --heads origin %current_branch% >nul 2>&1
if errorlevel 1 goto :push_branch

for /f "tokens=1,2" %%a in ('git rev-list --left-right --count %current_branch%...origin/%current_branch%') do (
    set "ahead_count=%%a"
    set "behind_count=%%b"
)

if not defined behind_count set "behind_count=0"
if %behind_count% GTR 0 (
    echo.
    echo Remote branch origin/%current_branch% has %behind_count% newer commit^(s^).
    set /p sync_now=Run git pull --rebase origin %current_branch% before push? (Y/n): 
    if /I "%sync_now%"=="N" (
        echo Push aborted. Sync your branch first, then rerun the script.
        goto :done
    )

    git pull --rebase origin %current_branch%
    if errorlevel 1 goto :rebase_conflict
)

:push_branch
echo.
echo Pushing to branch %current_branch%...
git push -u origin %current_branch%
if errorlevel 1 goto :error

echo.
echo ========================================
echo   PUSH COMPLETE!
echo ========================================
goto :done

:rebase_conflict
echo.
echo ========================================
echo   REBASE STOPPED DUE TO CONFLICTS
echo ========================================
echo Resolve the conflicted files, then run:
echo   git add ^<fixed-files^>
echo   git rebase --continue
echo.
echo If you want to cancel the rebase instead, run:
echo   git rebase --abort
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