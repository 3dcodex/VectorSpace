import os

# Define replacements
replacements = {
    r"{% url 'marketplace:my_assets' %}": "/dashboard/assets/",
    r"{% url 'marketplace:upload' %}": "/dashboard/assets/upload/",
    r"{% url 'marketplace:edit_asset'": "{% url 'marketplace:edit_asset'",  # Keep this one
    r"{% url 'games:my_games' %}": "/dashboard/games/",
    r"{% url 'games:publish' %}": "/dashboard/games/publish/",
    r"{% url 'jobs:my_applications' %}": "/dashboard/jobs/applications/",
    r"{% url 'jobs:post' %}": "/dashboard/jobs/post/",
    r"{% url 'jobs:recruiter_dashboard' %}": "/dashboard/jobs/recruiter/",
    r"{% url 'social:feed' %}": "/dashboard/social/",
    r"{% url 'social:create_post' %}": "/dashboard/social/post/create/",
    r"{% url 'social:messages' %}": "/dashboard/social/messages/",
    r"{% url 'mentorship:my_sessions' %}": "/dashboard/mentorship/",
    r"{% url 'mentorship:become_mentor' %}": "/dashboard/mentorship/become-mentor/",
    r"{% url 'competitions:create' %}": "/dashboard/competitions/create/",
}

templates_dir = r'c:\vector_space\templates'

def fix_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
    return False

# Walk through all HTML files
fixed_count = 0
for root, dirs, files in os.walk(templates_dir):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            if fix_file(filepath):
                fixed_count += 1
                print(f"Fixed: {filepath}")

print(f"\nTotal files fixed: {fixed_count}")
