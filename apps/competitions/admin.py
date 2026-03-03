from django.contrib import admin
from .models import Competition, Submission, Vote

admin.site.register(Competition)
admin.site.register(Submission)
admin.site.register(Vote)
