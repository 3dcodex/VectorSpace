from django import forms
from .models import Competition, Submission, Vote

class CompetitionForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = ['title', 'description', 'category', 'prize_pool', 'start_date', 'end_date', 'rules']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'rules': forms.Textarea(attrs={'rows': 6}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['title', 'description', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your submission...'}),
        }

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['score']
        widgets = {
            'score': forms.NumberInput(attrs={'min': 1, 'max': 10, 'placeholder': 'Rate 1-10'}),
        }
