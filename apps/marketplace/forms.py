from django import forms
from .models import Asset

class AssetUploadForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['title', 'description', 'asset_type', 'price', 'file', 'preview_image', 'file_format', 'category', 'tags', 'is_free', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter asset title'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Describe your asset...'}),
            'asset_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., Characters, Environments, Props'}),
            'file_format': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., FBX, OBJ, BLEND'}),
            'tags': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'character, low-poly, rigged'}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': '0.00', 'step': '0.01'}),
            'preview_image': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'https://example.com/image.jpg'}),
            'file': forms.FileInput(attrs={'class': 'form-file'}),
            'is_free': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if file.size > 104857600:
                raise forms.ValidationError('File size cannot exceed 100MB')
            allowed_extensions = ['.fbx', '.obj', '.blend', '.max', '.ma', '.mb', '.c4d', '.3ds', '.dae', '.gltf', '.glb', '.zip']
            file_ext = file.name.lower()[file.name.rfind('.'):]
            if file_ext not in allowed_extensions:
                raise forms.ValidationError(f'Unsupported file type. Allowed: {", ".join(allowed_extensions)}')
        return file
    
    def clean(self):
        cleaned_data = super().clean()
        is_free = cleaned_data.get('is_free')
        price = cleaned_data.get('price')
        if is_free:
            cleaned_data['price'] = 0
        elif not price or price <= 0:
            raise forms.ValidationError('Price must be greater than 0 for paid assets')
        return cleaned_data
