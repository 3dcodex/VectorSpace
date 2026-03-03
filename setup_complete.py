"""
Complete Vector Space Setup Script
Installs dependencies, runs migrations, and sets up the platform
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and print status"""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(result.stdout)
        print(f"✓ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} - FAILED")
        print(e.stderr)
        return False

def main():
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║         VECTOR SPACE - COMPLETE SETUP SCRIPT              ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Install Pillow
    if not run_command("python -m pip install Pillow", "Installing Pillow (ImageField support)"):
        print("\n⚠ Warning: Pillow installation failed. ImageField may not work.")
    
    # Step 2: Install all requirements
    if os.path.exists("requirements.txt"):
        run_command("pip install -r requirements.txt", "Installing all dependencies")
    
    # Step 3: Run migrations
    run_command("python manage.py makemigrations", "Creating migrations")
    run_command("python manage.py migrate", "Applying migrations")
    
    # Step 4: Create superuser prompt
    print(f"\n{'='*60}")
    print("CREATE SUPERUSER")
    print(f"{'='*60}")
    create_super = input("Do you want to create a superuser? (y/n): ").lower()
    if create_super == 'y':
        subprocess.run("python manage.py createsuperuser", shell=True)
    
    # Final message
    print(f"\n{'='*60}")
    print("✓ SETUP COMPLETE!")
    print(f"{'='*60}")
    print("\nNext steps:")
    print("  1. Run: python manage.py runserver")
    print("  2. Visit: http://localhost:8000")
    print("  3. Admin: http://localhost:8000/admin")
    print("\nOptional setup scripts:")
    print("  - python setup_marketplace.py  (Create categories)")
    print("  - python setup_roles.py        (Setup role system)")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
