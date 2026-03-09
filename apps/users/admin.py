from django.contrib import admin
from .models import User, UserProfile, UserSettings
from .reputation_models import RoleReputation, ServiceFlow, Badge, UserBadge, RoleReview

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(UserSettings)

@admin.register(RoleReputation)
class RoleReputationAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'score', 'trust_level', 'average_rating', 'services_provided')
    list_filter = ('role', 'trust_level', 'verified_badge')
    search_fields = ('user__username',)

@admin.register(ServiceFlow)
class ServiceFlowAdmin(admin.ModelAdmin):
    list_display = ('provider', 'consumer', 'service_type', 'value', 'rating', 'created_at')
    list_filter = ('service_type', 'completed')
    search_fields = ('provider__username', 'consumer__username', 'service_name')

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('icon', 'name', 'badge_type', 'rarity', 'required_score')
    list_filter = ('badge_type', 'rarity')

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'earned_at', 'displayed')
    list_filter = ('displayed',)

@admin.register(RoleReview)
class RoleReviewAdmin(admin.ModelAdmin):
    list_display = ('reviewer', 'reviewed_user', 'role_reviewed', 'rating', 'would_recommend')
    list_filter = ('role_reviewed', 'would_recommend', 'rating')
