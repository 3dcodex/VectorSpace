from django import forms
from .models import Post, Comment, Message

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'media']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Give your post an engaging title...'}),
            'content': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 8, 'placeholder': 'Share your thoughts, ideas, or questions with the community...'}),
            'category': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Game Development, 3D Modeling, Unity...'}),
            'media': forms.FileInput(attrs={'class': 'form-file'}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Add a comment...'}),
        }

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={'placeholder': 'Type a message...'}),
        }
