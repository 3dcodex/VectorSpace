# Quick Fix: Pillow Not Installed Error

## Error
```
marketplace.Asset.preview_image: (fields.E210) Cannot use ImageField because Pillow is not installed.
```

## Solution

### Option 1: Quick Fix (Windows)
```bash
python -m pip install Pillow
```

### Option 2: Use Install Script
```bash
python install_pillow.bat
```

### Option 3: Complete Setup
```bash
python setup_complete.py
```

This will:
- Install Pillow
- Install all dependencies
- Run migrations
- Prompt for superuser creation

## After Installation

Run the server:
```bash
python manage.py runserver
```

Visit: http://localhost:8000

## Why This Happened
The Asset model uses `ImageField` for `preview_image`, which requires the Pillow library for image processing. Pillow is listed in `requirements.txt` but wasn't installed in your virtual environment.

## Verify Installation
```bash
python -c "import PIL; print(PIL.__version__)"
```

Should output the Pillow version (e.g., 10.0.0 or higher).
