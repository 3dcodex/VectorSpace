from django.contrib import admin
from .models import Asset, Purchase, Review, Category, Transaction, Wallet
from .search_models import (
    SearchQuery, SavedSearch, TrendingItem, SearchFilter, 
    SimilarItem, DiscoveryCard, SearchAnalytics
)

admin.site.register(Asset)
admin.site.register(Purchase)
admin.site.register(Review)
admin.site.register(Category)
admin.site.register(Transaction)
admin.site.register(Wallet)


# Search & Discovery Admin

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query_text', 'search_type', 'user', 'results_count', 'clicked_result', 'created_at']
    list_filter = ['search_type', 'clicked_result', 'created_at']
    search_fields = ['query_text', 'user__username']
    readonly_fields = ['created_at', 'ip_address']


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'search_type', 'run_count', 'is_public', 'created_at']
    list_filter = ['search_type', 'is_public']
    search_fields = ['name', 'user__username', 'query_text']


@admin.register(TrendingItem)
class TrendingItemAdmin(admin.ModelAdmin):
    list_display = ['get_title', 'item_type', 'period', 'ranking', 'score', 'calculated_at']
    list_filter = ['item_type', 'period']
    search_fields = ['asset__title', 'game__title']
    readonly_fields = ['calculated_at']
    
    def get_title(self, obj):
        if obj.asset:
            return obj.asset.title
        return obj.game.title


@admin.register(SearchFilter)
class SearchFilterAdmin(admin.ModelAdmin):
    list_display = ['filter_type', 'label', 'value', 'asset_count', 'game_count', 'is_active', 'order']
    list_filter = ['filter_type', 'is_active']
    search_fields = ['label', 'value']


@admin.register(SimilarItem)
class SimilarItemAdmin(admin.ModelAdmin):
    list_display = ['source_asset', 'get_similar_title', 'similarity_score', 'rank']
    list_filter = ['similarity_score']
    search_fields = ['source_asset__title', 'similar_asset__title', 'similar_game__title']
    
    def get_similar_title(self, obj):
        if obj.similar_asset:
            return obj.similar_asset.title
        return obj.similar_game.title


@admin.register(DiscoveryCard)
class DiscoveryCardAdmin(admin.ModelAdmin):
    list_display = ['title', 'card_type', 'is_active', 'order', 'views', 'clicks']
    list_filter = ['card_type', 'is_active']
    search_fields = ['title', 'description']


@admin.register(SearchAnalytics)
class SearchAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_searches', 'unique_searchers', 'click_through_rate']
    list_filter = ['date']
    readonly_fields = ['date']
