"""
Dashboard Portfolio URLs - manage creator portfolio
"""
from django.urls import path
from apps.core import portfolio_views

urlpatterns = [
    path('', portfolio_views.my_portfolio, name='dashboard_my_portfolio'),
    path('', portfolio_views.my_portfolio, name='my_portfolio'),
    path('settings/', portfolio_views.edit_portfolio_settings, name='dashboard_edit_settings'),
    path('settings/', portfolio_views.edit_portfolio_settings, name='edit_settings'),
    path('analytics/', portfolio_views.portfolio_analytics, name='dashboard_portfolio_analytics'),
    path('analytics/', portfolio_views.portfolio_analytics, name='analytics'),
    
    # Featured items management
    path('featured/add/', portfolio_views.add_featured_item, name='dashboard_add_featured'),
    path('featured/add/', portfolio_views.add_featured_item, name='add_featured'),
    path('featured/remove/<int:item_id>/', portfolio_views.remove_featured_item, name='dashboard_remove_featured'),
    path('featured/remove/<int:item_id>/', portfolio_views.remove_featured_item, name='remove_featured'),
    path('featured/reorder/', portfolio_views.reorder_featured_items, name='dashboard_reorder_featured'),
    path('featured/reorder/', portfolio_views.reorder_featured_items, name='reorder_featured'),
    path('featured/showcase/<int:item_id>/', portfolio_views.toggle_featured_showcase, name='dashboard_toggle_showcase'),
    path('featured/showcase/<int:item_id>/', portfolio_views.toggle_featured_showcase, name='toggle_showcase'),
    
    # Testimonials
    path('testimonials/', portfolio_views.manage_testimonials, name='dashboard_manage_testimonials'),
    path('testimonials/', portfolio_views.manage_testimonials, name='manage_testimonials'),
    path('testimonials/add/', portfolio_views.add_testimonial, name='dashboard_add_testimonial'),
    path('testimonials/add/', portfolio_views.add_testimonial, name='add_testimonial'),
    path('testimonials/delete/<int:testimonial_id>/', portfolio_views.delete_testimonial, name='dashboard_delete_testimonial'),
    path('testimonials/delete/<int:testimonial_id>/', portfolio_views.delete_testimonial, name='delete_testimonial'),
]
