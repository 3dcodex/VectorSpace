from django import forms
from .models import MentorProfile, MentorshipRequest, Session

class MentorProfileForm(forms.ModelForm):
    class Meta:
        model = MentorProfile
        fields = ['expertise', 'hourly_rate', 'available']
        widgets = {
            'expertise': forms.TextInput(attrs={
                'placeholder': 'Enter expertise as JSON array, e.g., ["3D Modeling", "Animation", "Rigging"]'
            }),
        }
    
    def clean_expertise(self):
        expertise = self.cleaned_data.get('expertise')
        if isinstance(expertise, str):
            import json
            try:
                expertise = json.loads(expertise)
            except json.JSONDecodeError:
                expertise = [e.strip() for e in expertise.split(',') if e.strip()]
        return expertise

class SessionBookingForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['scheduled_at', 'duration_minutes']
        widgets = {
            'scheduled_at': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'datetime-input'
            }),
            'duration_minutes': forms.Select(choices=[
                (30, '30 minutes'),
                (60, '1 hour'),
                (90, '1.5 hours'),
                (120, '2 hours'),
            ])
        }

class MentorshipRequestForm(forms.ModelForm):
    class Meta:
        model = MentorshipRequest
        fields = ['topic', 'description']
        widgets = {
            'topic': forms.TextInput(attrs={
                'placeholder': 'e.g., Character Modeling Techniques'
            }),
            'description': forms.Textarea(attrs={
                'rows': 6,
                'placeholder': 'Describe what you want to learn and your current skill level...'
            }),
        }
