@echo off
REM Optional Cleanup Script for Vector Space
REM This removes redundant files and organizes development scripts

echo ========================================
echo Vector Space - Optional Cleanup
echo ========================================
echo.
echo This script will:
echo 1. Remove empty template folders
echo 2. Organize development .bat files into scripts folder
echo 3. Keep only essential scripts in root
echo.
echo Press Ctrl+C to cancel, or
pause

echo.
echo [1/3] Removing empty template folders...
if exist "templates\public\games" rmdir "templates\public\games"
if exist "templates\public\jobs" rmdir "templates\public\jobs"
if exist "templates\public\marketplace" rmdir "templates\public\marketplace"
if exist "templates\public\social" rmdir "templates\public\social"
if exist "templates\dashboard\games" rmdir "templates\dashboard\games"
if exist "templates\dashboard\jobs" rmdir "templates\dashboard\jobs"
if exist "templates\dashboard\marketplace" rmdir "templates\dashboard\marketplace"
if exist "templates\dashboard\mentorship" rmdir "templates\dashboard\mentorship"
if exist "templates\dashboard\social" rmdir "templates\dashboard\social"
if exist "templates\public" rmdir "templates\public"
if exist "templates\dashboard" rmdir "templates\dashboard"
echo Done!

echo.
echo [2/3] Creating scripts folder...
if not exist "scripts" mkdir "scripts"
echo Done!

echo.
echo [3/3] Moving development scripts...
if exist "fix.bat" move "fix.bat" "scripts\"
if exist "FIX_ALL_ERRORS.bat" move "FIX_ALL_ERRORS.bat" "scripts\"
if exist "fix_db.bat" move "fix_db.bat" "scripts\"
if exist "fix_errors.bat" move "fix_errors.bat" "scripts\"
if exist "install_pillow.bat" move "install_pillow.bat" "scripts\"
if exist "setup_community.bat" move "setup_community.bat" "scripts\"
if exist "setup_marketplace_enhancements.bat" move "setup_marketplace_enhancements.bat" "scripts\"
echo Done!

echo.
echo ========================================
echo Cleanup Complete!
echo ========================================
echo.
echo Kept in root:
echo - push_sjeff.bat (useful for git automation)
echo - setup_db.bat (useful for database setup)
echo.
echo Moved to scripts/:
echo - All fix_*.bat files
echo - All setup_*.bat files (except setup_db.bat)
echo - install_pillow.bat
echo.
echo Your project is now cleaner!
echo.
pause
