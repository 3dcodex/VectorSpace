from django.db import models
from apps.users.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name

class Asset(models.Model):
    ASSET_TYPES = [
        ('3d_model', '3D Model'),
        ('texture', 'Texture'),
        ('plugin', 'Plugin'),
        ('script', 'Script'),
        ('sound', 'Sound'),
        ('vfx', 'VFX'),
        ('material', 'Material'),
        ('animation', 'Animation'),
        ('other', 'Other'),
    ]
    FILE_FORMATS = [
        ('OBJ', 'OBJ'),
        ('FBX', 'FBX'),
        ('BLEND', 'Blender'),
        ('GLTF', 'GLTF'),
        ('GLB', 'GLB'),
        ('MAX', '3DS Max'),
        ('MA', 'Maya'),
        ('C4D', 'Cinema 4D'),
    ]
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assets')
    title = models.CharField(max_length=200)
    description = models.TextField()
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    file = models.FileField(upload_to='asset_files/')
    preview_image = models.CharField(max_length=500, blank=True, null=True)  # Temporary: URL instead of ImageField
    file_format = models.CharField(max_length=10, choices=FILE_FORMATS, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.CharField(max_length=255, blank=True, help_text='Comma-separated tags')
    downloads = models.IntegerField(default=0)
    rating = models.FloatField(default=0)
    featured = models.BooleanField(default=False)
    is_free = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=50, blank=True, default='1.0')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

class Purchase(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    purchased_at = models.DateTimeField(auto_now_add=True)

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    TRANSACTION_TYPE = [
        ('asset_purchase', 'Asset Purchase'),
        ('mentorship_payment', 'Mentorship Payment'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    stripe_payment_id = models.CharField(max_length=255, blank=True)
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

