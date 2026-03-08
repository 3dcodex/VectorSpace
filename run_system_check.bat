@echo off
echo ========================================
echo Vector Space - System Check
echo ========================================
echo.

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo Warning: Virtual environment not found
)

echo.
echo Running comprehensive system check...
echo.

python scripts\utils\system_check.py

echo.
echo ========================================
echo System check complete!
echo ========================================
echo.

pause
