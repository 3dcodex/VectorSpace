from django import forms
from .models import Game

class GamePublishForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['title', 'description', 'genre', 'build_file', 'thumbnail']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Describe your game...'}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g., Space Adventure'}),
            'genre': forms.TextInput(attrs={'placeholder': 'e.g., Action, RPG, Puzzle'}),
            'thumbnail': forms.TextInput(attrs={'placeholder': 'Image URL'}),
        }
    
    def clean_build_file(self):
        file = self.cleaned_data.get('build_file')
        if file:
            if file.size > 524288000:  # 500MB
                raise forms.ValidationError('Build file cannot exceed 500MB')
        return file
