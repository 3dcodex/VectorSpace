from django.contrib import admin
from .models import Asset, Purchase, Review, Category, Transaction, Wallet

admin.site.register(Asset)
admin.site.register(Purchase)
admin.site.register(Review)
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(Wallet)
