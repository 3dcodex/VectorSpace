"""
File upload validators for security
"""
import os
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible

ALLOWED_ASSET_EXTENSIONS = [
    '.fbx', '.obj', '.blend', '.gltf', '.glb',
    '.max', '.ma', '.c4d', '.zip', '.rar', '.7z',
    '.png', '.jpg', '.jpeg', '.gif', '.webp',
    '.mp3', '.wav', '.ogg', '.flac',
    '.mp4', '.mov', '.avi', '.mkv',
    '.txt', '.pdf', '.md'
]

DANGEROUS_EXTENSIONS = [
    '.exe', '.bat', '.sh', '.cmd', '.com', '.pif',
    '.scr', '.vbs', '.js', '.jar', '.app', '.deb',
    '.rpm', '.dmg', '.pkg', '.msi', '.php', '.asp',
    '.aspx', '.jsp', '.py', '.rb', '.pl'
]

MAX_ASSET_SIZE = 500 * 1024 * 1024  # 500MB
MAX_IMAGE_SIZE = 10 * 1024 * 1024   # 10MB
MAX_AUDIO_SIZE = 50 * 1024 * 1024   # 50MB

@deconstructible
class FileValidator:
    def __init__(self, allowed_extensions=None, max_size=None):
        self.allowed_extensions = allowed_extensions or ALLOWED_ASSET_EXTENSIONS
        self.max_size = max_size or MAX_ASSET_SIZE
    
    def __call__(self, file):
        # Check extension
        ext = os.path.splitext(file.name)[1].lower()
        
        # Block dangerous files
        if ext in DANGEROUS_EXTENSIONS:
            raise ValidationError(
                f'File type "{ext}" is not allowed for security reasons.'
            )
        
        # Check if extension is allowed
        if ext not in self.allowed_extensions:
            raise ValidationError(
                f'File type "{ext}" is not allowed. '
                f'Allowed types: {", ".join(self.allowed_extensions)}'
            )
        
        # Check size
        if file.size > self.max_size:
            max_mb = self.max_size / (1024 * 1024)
            file_mb = file.size / (1024 * 1024)
            raise ValidationError(
                f'File size ({file_mb:.1f}MB) exceeds maximum allowed size of {max_mb:.0f}MB'
            )
        
        return file

validate_asset_file = FileValidator()
validate_image_file = FileValidator(
    allowed_extensions=['.png', '.jpg', '.jpeg', '.gif', '.webp'],
    max_size=MAX_IMAGE_SIZE
)
