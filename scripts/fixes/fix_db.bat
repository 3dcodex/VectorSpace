@echo off
echo ========================================
echo  FIXING ALL DATABASE ERRORS
echo ========================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Step 1: Making migrations...
python manage.py makemigrations

echo.
echo Step 2: Running migrations...
python manage.py migrate

echo.
echo ========================================
echo  DONE!
echo ========================================
echo.
echo Your database is now fixed.
echo Run: python manage.py runserver
echo.
pause
