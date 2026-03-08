from django.contrib import admin
from apps.core.portfolio_models import (
    CreatorPortfolio, FeaturedItem, Achievement, 
    PortfolioSection, Testimonial, PortfolioAnalytics
)
from apps.core.notifications import Notification, NotificationPreference


@admin.register(CreatorPortfolio)
class CreatorPortfolioAdmin(admin.ModelAdmin):
    list_display = ['user', 'custom_url', 'is_public', 'total_views', 'total_projects', 'verified_creator']
    list_filter = ['is_public', 'verified_creator', 'featured_by_platform']
    search_fields = ['user__username', 'user__email', 'tagline', 'custom_url']
    readonly_fields = ['total_views', 'total_likes', 'total_downloads', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Settings', {
            'fields': ('is_public', 'custom_url', 'tagline', 'specialties', 'years_experience')
        }),
        ('Branding', {
            'fields': ('cover_image', 'primary_color')
        }),
        ('Stats', {
            'fields': ('total_views', 'total_likes', 'total_downloads', 'total_revenue')
        }),
        ('Platform', {
            'fields': ('featured_by_platform', 'verified_creator')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'last_activity')
        }),
    )


@admin.register(FeaturedItem)
class FeaturedItemAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'item_type', 'get_title', 'order', 'is_showcase', 'created_at']
    list_filter = ['item_type', 'is_showcase']
    search_fields = ['portfolio__user__username', 'asset__title', 'game__title']
    ordering = ['order', '-created_at']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'title', 'achievement_type', 'is_visible', 'is_rare', 'earned_at']
    list_filter = ['achievement_type', 'is_visible', 'is_rare']
    search_fields = ['portfolio__user__username', 'title', 'description']
    ordering = ['-earned_at']


@admin.register(PortfolioSection)
class PortfolioSectionAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'title', 'order', 'is_visible', 'created_at']
    list_filter = ['is_visible']
    search_fields = ['portfolio__user__username', 'title']
    ordering = ['order']


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'author_name', 'rating', 'is_featured', 'is_approved', 'created_at']
    list_filter = ['is_featured', 'is_approved', 'rating']
    search_fields = ['portfolio__user__username', 'author_name', 'content']
    ordering = ['-created_at']
    actions = ['approve_testimonials', 'feature_testimonials']
    
    def approve_testimonials(self, request, queryset):
        queryset.update(is_approved=True)
    approve_testimonials.short_description = "Approve selected testimonials"
    
    def feature_testimonials(self, request, queryset):
        queryset.update(is_featured=True)
    feature_testimonials.short_description = "Feature selected testimonials"


@admin.register(PortfolioAnalytics)
class PortfolioAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['portfolio', 'date', 'views', 'unique_visitors', 'downloads', 'revenue']
    list_filter = ['date']
    search_fields = ['portfolio__user__username']
    ordering = ['-date']
    readonly_fields = ['portfolio', 'date', 'views', 'unique_visitors', 'likes', 'shares', 'downloads', 'revenue']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'priority', 'read', 'created_at']
    list_filter = ['notification_type', 'priority', 'read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    readonly_fields = ['user', 'created_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('user', 'notification_type', 'title', 'message')
        }),
        ('Links & Actions', {
            'fields': ('link', 'action_url')
        }),
        ('Metadata', {
            'fields': ('priority', 'read', 'related_object_id', 'related_object_type', 'created_at')
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        queryset.update(read=True)
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        queryset.update(read=False)
    mark_as_unread.short_description = "Mark selected notifications as unread"


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_notifications', 'push_notifications', 'marketplace_notifications', 'social_notifications']
    list_filter = ['email_notifications', 'push_notifications', 'marketplace_notifications', 'social_notifications']
    search_fields = ['user__username', 'user__email']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Delivery Preferences', {
            'fields': ('email_notifications', 'push_notifications')
        }),
        ('Notification Types', {
            'fields': ('marketplace_notifications', 'social_notifications', 'job_notifications', 'mentorship_notifications', 'system_notifications')
        }),
    )
