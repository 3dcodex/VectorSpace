from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserProfile

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    primary_role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES, 
        required=True,
        help_text="Your main role - defines your primary dashboard experience"
    )
    secondary_roles = forms.MultipleChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple,
        help_text="Additional roles you want to perform (e.g., Developer + Creator)"
    )
    
    # Common fields
    location = forms.CharField(max_length=100, required=False)
    experience_years = forms.IntegerField(required=False, initial=0, min_value=0)
    
    # Social links
    github = forms.URLField(required=False)
    linkedin = forms.URLField(required=False)
    portfolio_url = forms.URLField(required=False)
    
    # Creator-specific
    specialization = forms.CharField(max_length=100, required=False, help_text="e.g., 3D Artist, VFX Designer")
    
    # Developer-specific
    programming_languages = forms.CharField(required=False, help_text="Comma-separated (e.g., C#, Python, C++)")
    game_engines = forms.CharField(required=False, help_text="Comma-separated (e.g., Unity, Unreal, Godot)")
    
    # Recruiter-specific
    company_name = forms.CharField(max_length=200, required=False)
    company_website = forms.URLField(required=False)
    company_size = forms.CharField(max_length=50, required=False)
    
    # Mentor-specific
    expertise_areas = forms.CharField(required=False, help_text="Comma-separated areas of expertise")
    hourly_rate = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Email already registered')
        return email
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.portfolio_url = self.cleaned_data.get('portfolio_url', '')
        
        if commit:
            user.save()
            profile = user.profile
            
            # Set multi-role system
            primary = self.cleaned_data['primary_role']
            secondary = list(self.cleaned_data.get('secondary_roles', []))
            
            # Remove primary from secondary if accidentally selected
            if primary in secondary:
                secondary.remove(primary)
            
            profile.primary_role = primary
            profile.secondary_roles = secondary
            profile.role = primary  # Backward compatibility
            
            profile.location = self.cleaned_data.get('location', '')
            profile.experience_years = self.cleaned_data.get('experience_years', 0)
            profile.github = self.cleaned_data.get('github', '')
            profile.linkedin = self.cleaned_data.get('linkedin', '')
            
            # Save role-specific fields based on any role user has
            all_roles = [primary] + secondary
            
            if 'CREATOR' in all_roles:
                profile.specialization = self.cleaned_data.get('specialization', '')
            
            if 'DEVELOPER' in all_roles:
                prog_langs = self.cleaned_data.get('programming_languages', '')
                profile.programming_languages = [lang.strip() for lang in prog_langs.split(',')] if prog_langs else []
                engines = self.cleaned_data.get('game_engines', '')
                profile.game_engines = [eng.strip() for eng in engines.split(',')] if engines else []
            
            if 'RECRUITER' in all_roles:
                profile.company_name = self.cleaned_data.get('company_name', '')
                profile.company_website = self.cleaned_data.get('company_website', '')
                profile.company_size = self.cleaned_data.get('company_size', '')
            
            if 'MENTOR' in all_roles:
                expertise = self.cleaned_data.get('expertise_areas', '')
                profile.expertise_areas = [area.strip() for area in expertise.split(',')] if expertise else []
                profile.hourly_rate = self.cleaned_data.get('hourly_rate')
            
            profile.save()
        
        return user
