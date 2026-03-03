from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    path('', views.feed, name='feed'),
    path('post/create/', views.create_post, name='create_post'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
    path('post/<int:pk>/vote/<str:vote_type>/', views.vote_post, name='vote_post'),
    path('post/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('messages/', views.messages_list, name='messages'),
    path('messages/<int:user_id>/', views.conversation, name='conversation'),
    path('profile/<int:user_id>/', views.user_profile, name='profile'),
    path('follow/<int:user_id>/', views.follow_user, name='follow'),
]
