import os
import shutil

# Clear __pycache__ directories
for root, dirs, files in os.walk('.'):
    if '__pycache__' in dirs:
        cache_path = os.path.join(root, '__pycache__')
        print(f'Removing {cache_path}')
        shutil.rmtree(cache_path)

print('Cache cleared!')
