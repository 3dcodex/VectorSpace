from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    user_type = forms.ChoiceField(choices=User.USER_TYPES, required=True)
    role = forms.ChoiceField(choices=UserProfile.ROLE_CHOICES, required=True, initial='USER')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'user_type', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile = user.profile
            profile.role = self.cleaned_data['role']
            profile.save()
        return user
