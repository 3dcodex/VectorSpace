from django import forms
from .models import Asset

class AssetUploadForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['title', 'description', 'asset_type', 'price', 'file', 'preview_image', 'file_format', 'category', 'tags', 'is_free', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your asset...'}),
            'tags': forms.TextInput(attrs={'placeholder': 'e.g., character, low-poly, rigged'}),
            'title': forms.TextInput(attrs={'placeholder': 'Asset title'}),
            'price': forms.NumberInput(attrs={'placeholder': '0.00', 'step': '0.01'}),
            'preview_image': forms.TextInput(attrs={'placeholder': 'Image URL (e.g., https://example.com/image.jpg)'}),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Validate file size (max 100MB)
            if file.size > 104857600:
                raise forms.ValidationError('File size cannot exceed 100MB')
            
            # Validate file type for 3D models
            allowed_extensions = ['.fbx', '.obj', '.blend', '.max', '.ma', '.mb', '.c4d', '.3ds', '.dae', '.gltf', '.glb']
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
