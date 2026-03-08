@echo off
echo ========================================
echo  FIXING ALL ERRORS
echo ========================================
echo.

echo Creating all migrations...
python manage.py makemigrations
echo.

echo Running migrations...
python manage.py migrate
echo.

echo ========================================
echo  DONE! Try running the server now.
echo ========================================
pause
