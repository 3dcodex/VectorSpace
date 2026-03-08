# Marketplace Model Setup - Quick Guide

## What Changed
✅ Added `Category` model for organizing assets
✅ Added `file_format` field (OBJ, FBX, BLEND, GLTF, etc.)
✅ Added `is_active` field for publishing control
✅ Changed `preview_image` from CharField to ImageField
✅ Updated file upload paths for better organization

## Setup Instructions

### Option 1: Automated Setup (Recommended)
```bash
python setup_marketplace.py
```
This will:
- Apply all migrations
- Create sample categories (Characters, Environments, Props, Vehicles, Weapons, Architecture)

### Option 2: Manual Setup
```bash
# Apply migrations
python manage.py migrate marketplace

# Create categories in Django admin or shell
python manage.py shell
>>> from apps.marketplace.models import Category
>>> Category.objects.create(name='Characters')
>>> Category.objects.create(name='Environments')
# ... etc
```

## Model Structure

### Asset Model Fields
- `seller` - ForeignKey to User
- `title` - CharField(200)
- `description` - TextField
- `asset_type` - Choice field (3d_model, texture, plugin, etc.)
- `price` - DecimalField
- `file` - FileField (uploads to asset_files/)
- `preview_image` - ImageField (uploads to asset_thumbnails/)
- `file_format` - Choice field (OBJ, FBX, BLEND, GLTF, etc.)
- `category` - ForeignKey to Category (optional)
- `tags` - CharField (comma-separated)
- `downloads` - IntegerField (default=0)
- `rating` - FloatField (default=0)
- `featured` - BooleanField (default=False)
- `is_free` - BooleanField (default=False)
- `is_active` - BooleanField (default=True)
- `version` - CharField (default='1.0')
- `created_at` - DateTimeField (auto)
- `updated_at` - DateTimeField (auto)

### Category Model
- `name` - CharField(100)

## Admin Panel
All models are registered in admin:
- Asset
- Category
- Purchase
- Review
- Transaction
- Wallet

Access at: http://localhost:8000/admin/

## Upload Assets
- URL: /marketplace/upload/
- Form includes all new fields
- File validation: max 100MB, 3D formats only
- Image validation: standard image formats

## Browse Marketplace
- URL: /marketplace/
- Features: search, filter by price, sort, pagination
- Shows 12 assets per page
- Fully database-driven (no fake data)
