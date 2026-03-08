from django.contrib import admin
from .models import Post, Comment, Follow, Message, Category, PostVote, PostLike

admin.site.register(Category)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Follow)
admin.site.register(Message)
admin.site.register(PostVote)
admin.site.register(PostLike)
