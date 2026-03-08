from django.urls import path
from apps.dashboard.views import social

urlpatterns = [
    path('feed/', social.feed, name='social_feed'),
    path('my-posts/', social.my_posts, name='social_my_posts'),
    path('my-profile/', social.my_profile, name='social_my_profile'),
    path('profile/<int:user_id>/', social.user_profile, name='social_profile'),
    path('edit-profile/', social.edit_profile, name='social_edit_profile'),
    path('settings/', social.settings, name='social_settings'),
    path('post/create/', social.create_post, name='social_create_post'),
    path('post/<int:pk>/like/', social.like_post, name='social_like_post'),
    path('post/<int:pk>/vote/<str:vote_type>/', social.vote_post, name='social_vote_post'),
    path('post/<int:pk>/comment/', social.add_comment, name='social_add_comment'),
    path('messages/', social.messages_list, name='social_messages'),
    path('messages/<int:user_id>/', social.conversation, name='social_conversation'),
    path('follow/<int:user_id>/', social.follow_user, name='social_follow'),
]
