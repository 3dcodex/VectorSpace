from django.db import models
from apps.users.models import User

class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations')
    title = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    ROLES = [('user', 'User'), ('assistant', 'Assistant')]
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class AIAssistant(models.Model):
    TYPES = [('code', 'Code Helper'), ('art', 'Art Advisor'), ('game', 'Game Design'), ('career', 'Career Guide')]
    name = models.CharField(max_length=100)
    assistant_type = models.CharField(max_length=20, choices=TYPES)
    description = models.TextField()
    active = models.BooleanField(default=True)
