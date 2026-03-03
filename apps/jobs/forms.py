from django import forms
from .models import Job, Application

class JobPostForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'job_type', 'location', 'remote', 
                  'salary_min', 'salary_max', 'required_skills']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6, 'placeholder': 'Describe the role, responsibilities, and requirements...'}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g., Senior 3D Artist'}),
            'location': forms.TextInput(attrs={'placeholder': 'e.g., Los Angeles, CA'}),
            'required_skills': forms.TextInput(attrs={'placeholder': 'Enter skills as JSON array, e.g., ["Blender", "Maya", "ZBrush"]'}),
        }
    
    def clean_required_skills(self):
        skills = self.cleaned_data.get('required_skills')
        if isinstance(skills, str):
            import json
            try:
                skills = json.loads(skills)
            except json.JSONDecodeError:
                # If not valid JSON, split by comma
                skills = [s.strip() for s in skills.split(',') if s.strip()]
        return skills

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'resume']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 8, 
                'placeholder': 'Tell the recruiter why you\'re a great fit for this role...'
            }),
        }
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            # Validate file size (max 5MB)
            if resume.size > 5242880:
                raise forms.ValidationError('Resume file size cannot exceed 5MB')
            
            # Validate file type
            allowed_extensions = ['.pdf', '.doc', '.docx']
            file_ext = resume.name.lower()[resume.name.rfind('.'):]
            if file_ext not in allowed_extensions:
                raise forms.ValidationError(f'Unsupported file type. Allowed: {", ".join(allowed_extensions)}')
        
        return resume

class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'status-select'})
        }
