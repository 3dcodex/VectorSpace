from django.db import models
from django.urls import reverse
from django.utils.text import slugify
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
    SOFTWARE = [
        ('blender', 'Blender'),
        ('unreal', 'Unreal Engine'),
        ('unity', 'Unity'),
        ('maya', 'Maya'),
        ('3dsmax', '3DS Max'),
        ('c4d', 'Cinema 4D'),
    ]
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assets')
    title = models.CharField(max_length=200)
    description = models.TextField()
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    file = models.FileField(upload_to='asset_files/')
    preview_image = models.CharField(max_length=500, blank=True, null=True)
    file_format = models.CharField(max_length=10, choices=FILE_FORMATS, blank=True)
    software = models.CharField(max_length=20, choices=SOFTWARE, blank=True)
    poly_count = models.IntegerField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.CharField(max_length=255, blank=True, help_text='Comma-separated tags')
    downloads = models.IntegerField(default=0)
    view_count = models.IntegerField(default=0)  # Track page views for recommendations
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
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases', db_index=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, db_index=True)
    price_paid = models.DecimalField(max_digits=10, decimal_places=2)
    purchased_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['buyer', '-purchased_at']),
            models.Index(fields=['asset', '-purchased_at']),
        ]

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

class Wishlist(models.Model):
    """
    Tracks assets that users want to purchase or keep for later.
    Simple many-to-many relationship between Users and Assets.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'asset')
        ordering = ['-added_at']  # Show newest additions first
    
    def __str__(self):
        return f"{self.user.username} - {self.asset.title}"


class Collection(models.Model):
    """
    Named collections of assets that users can create and organize.
    Collections can be private or public, allowing users to showcase their curated sets.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, blank=True)  # URL-friendly version of name
    description = models.TextField(blank=True, help_text="Optional description of this collection")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collections')
    
    # Privacy settings
    is_public = models.BooleanField(
        default=False, 
        help_text="Whether this collection is visible to other users"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('owner', 'slug')  # Each user can have uniquely named collections
        ordering = ['-updated_at']
    
    def save(self, *args, **kwargs):
        """Auto-generate slug from name if not provided"""
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            # Ensure unique slug for this user
            while Collection.objects.filter(owner=self.owner, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """URL for viewing this collection"""
        return reverse('marketplace:collection_detail', kwargs={
            'username': self.owner.username, 
            'slug': self.slug
        })
    
    def asset_count(self):
        """Return the number of assets in this collection"""
        return self.items.count()
    
    def __str__(self):
        return f"{self.owner.username}'s {self.name}"


class CollectionItem(models.Model):
    """
    Individual assets within a collection.
    This through-model allows for ordering and additional metadata.
    """
    collection = models.ForeignKey(
        Collection, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    
    # Ordering and metadata
    position = models.PositiveIntegerField(
        default=0, 
        help_text="Position within the collection for custom ordering"
    )
    added_at = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(
        max_length=255, 
        blank=True, 
        help_text="Optional personal notes about this asset"
    )
    
    class Meta:
        unique_together = ('collection', 'asset')  # Can't add same asset twice to one collection
        ordering = ['position', '-added_at']  # Custom order, then newest first
    
    def __str__(self):
        return f"{self.asset.title} in {self.collection.name}"

