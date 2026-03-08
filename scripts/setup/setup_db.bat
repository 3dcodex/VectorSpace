@echo off
echo Setting up Vector Space database...
echo.

echo Step 1: Making migrations...
python manage.py makemigrations
echo.

echo Step 2: Running migrations...
python manage.py migrate
echo.

echo Step 3: Database setup complete!
echo.
echo You can now run: python manage.py runserver
pause
