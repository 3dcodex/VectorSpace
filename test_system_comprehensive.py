"""
Comprehensive System Test Script
Tests all URLs, functionality, and security measures
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from apps.users.models import UserProfile
from apps.marketplace.models import Asset, Category
from apps.games.models import Game
from apps.jobs.models import Job
from apps.mentorship.models import MentorProfile
from apps.social.models import Post
from apps.competitions.models import Competition
from colorama import init, Fore, Style
import traceback

init(autoreset=True)

User = get_user_model()

class SystemTester:
    def __init__(self):
        self.client = Client()
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def print_header(self, text):
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}{text}")
        print(f"{Fore.CYAN}{'='*60}\n")
    
    def print_success(self, text):
        print(f"{Fore.GREEN}✓ {text}")
        self.passed += 1
    
    def print_error(self, text, error=None):
        print(f"{Fore.RED}✗ {text}")
        if error:
            print(f"{Fore.YELLOW}  Error: {error}")
            self.errors.append((text, str(error)))
        self.failed += 1
    
    def print_info(self, text):
        print(f"{Fore.YELLOW}ℹ {text}")
    
    def test_url(self, name, url, expected_status=200, method='GET', data=None, auth_required=False):
        """Test a single URL"""
        try:
            if method == 'GET':
                response = self.client.get(url)
            elif method == 'POST':
                response = self.client.post(url, data or {})
            
            if auth_required and response.status_code == 302:
                # Redirect to login is expected for auth-required pages
                self.print_success(f"{name}: Redirects to login (auth required)")
                return True
            
            if response.status_code == expected_status:
                self.print_success(f"{name}: {url} [{response.status_code}]")
                return True
            else:
                self.print_error(f"{name}: {url}", f"Expected {expected_status}, got {response.status_code}")
                return False
        except Exception as e:
            self.print_error(f"{name}: {url}", str(e))
            return False
    
    def test_public_urls(self):
        """Test all public URLs"""
        self.print_header("Testing Public URLs")
        
        urls = [
            ("Home", "/", 200),
            ("Marketplace List", "/marketplace/", 200),
            ("Games List", "/games/", 200),
            ("Jobs List", "/jobs/", 200),
            ("Mentorship List", "/mentorship/", 200),
            ("Community", "/community/", 200),
            ("Competitions", "/competitions/", 200),
            ("Login", "/auth/login/", 200),
            ("Signup", "/auth/signup/", 200),
            ("AI Assistant", "/ai/", 200),
        ]
        
        for name, url, status in urls:
            self.test_url(name, url, status)
    
    def test_dashboard_urls(self):
        """Test dashboard URLs (should redirect to login)"""
        self.print_header("Testing Dashboard URLs (Auth Required)")
        
        urls = [
            ("Dashboard Overview", "/dashboard/", True),
            ("Dashboard Profile", "/dashboard/profile/", True),
            ("Dashboard Settings", "/dashboard/settings/", True),
            ("Dashboard Notifications", "/dashboard/notifications/", True),
            ("Marketplace Dashboard", "/dashboard/marketplace/", True),
            ("Games Dashboard", "/dashboard/games/", True),
            ("Jobs Dashboard", "/dashboard/jobs/", True),
        ]
        
        for name, url, auth_req in urls:
            self.test_url(name, url, 302, auth_required=auth_req)
    
    def test_api_endpoints(self):
        """Test API endpoints"""
        self.print_header("Testing API Endpoints")
        
        urls = [
            ("API Assets", "/api/v1/assets/", 200),
            ("API Games", "/api/v1/games/", 200),
            ("API Jobs", "/api/v1/jobs/", 200),
            ("API Mentors", "/api/v1/mentors/", 200),
            ("API Posts", "/api/v1/posts/", 200),
            ("API Competitions", "/api/v1/competitions/", 200),
        ]
        
        for name, url, status in urls:
            self.test_url(name, url, status)
    
    def test_database_models(self):
        """Test database models"""
        self.print_header("Testing Database Models")
        
        try:
            # Test User model
            user_count = User.objects.count()
            self.print_success(f"User model: {user_count} users")
            
            # Test UserProfile model
            profile_count = UserProfile.objects.count()
            self.print_success(f"UserProfile model: {profile_count} profiles")
            
            # Test Asset model
            asset_count = Asset.objects.count()
            self.print_success(f"Asset model: {asset_count} assets")
            
            # Test Game model
            game_count = Game.objects.count()
            self.print_success(f"Game model: {game_count} games")
            
            # Test Job model
            job_count = Job.objects.count()
            self.print_success(f"Job model: {job_count} jobs")
            
            # Test Post model
            post_count = Post.objects.count()
            self.print_success(f"Post model: {post_count} posts")
            
            # Test Competition model
            comp_count = Competition.objects.count()
            self.print_success(f"Competition model: {comp_count} competitions")
            
        except Exception as e:
            self.print_error("Database models test", str(e))
    
    def test_security_settings(self):
        """Test security settings"""
        self.print_header("Testing Security Settings")
        
        from django.conf import settings
        
        # Check SECRET_KEY
        if settings.SECRET_KEY and settings.SECRET_KEY != 'django-insecure-change-this-in-production':
            self.print_success("SECRET_KEY is configured")
        else:
            self.print_error("SECRET_KEY", "Using default or insecure key")
        
        # Check DEBUG
        if not settings.DEBUG:
            self.print_success("DEBUG is False (production mode)")
        else:
            self.print_info("DEBUG is True (development mode)")
        
        # Check ALLOWED_HOSTS
        if settings.ALLOWED_HOSTS and '*' not in settings.ALLOWED_HOSTS:
            self.print_success(f"ALLOWED_HOSTS configured: {settings.ALLOWED_HOSTS}")
        else:
            self.print_error("ALLOWED_HOSTS", "Allows all hosts (security risk)")
        
        # Check password validators
        if len(settings.AUTH_PASSWORD_VALIDATORS) >= 4:
            self.print_success(f"Password validators: {len(settings.AUTH_PASSWORD_VALIDATORS)} configured")
        else:
            self.print_error("Password validators", "Insufficient validators")
        
        # Check REST Framework throttling
        if 'DEFAULT_THROTTLE_CLASSES' in settings.REST_FRAMEWORK:
            self.print_success("API rate limiting configured")
        else:
            self.print_error("API rate limiting", "Not configured")
    
    def test_file_validators(self):
        """Test file upload validators"""
        self.print_header("Testing File Upload Validators")
        
        try:
            from apps.marketplace.validators import validate_asset_file, DANGEROUS_EXTENSIONS
            self.print_success(f"File validators imported successfully")
            self.print_success(f"Dangerous extensions blocked: {len(DANGEROUS_EXTENSIONS)}")
        except ImportError as e:
            self.print_error("File validators", str(e))
    
    def test_authentication_flow(self):
        """Test authentication flow"""
        self.print_header("Testing Authentication Flow")
        
        try:
            # Test signup page loads
            response = self.client.get('/auth/signup/')
            if response.status_code == 200:
                self.print_success("Signup page loads")
            else:
                self.print_error("Signup page", f"Status {response.status_code}")
            
            # Test login page loads
            response = self.client.get('/auth/login/')
            if response.status_code == 200:
                self.print_success("Login page loads")
            else:
                self.print_error("Login page", f"Status {response.status_code}")
            
            # Test logout redirects
            response = self.client.get('/auth/logout/')
            if response.status_code in [200, 302]:
                self.print_success("Logout works")
            else:
                self.print_error("Logout", f"Status {response.status_code}")
                
        except Exception as e:
            self.print_error("Authentication flow", str(e))
    
    def test_search_functionality(self):
        """Test search with various inputs"""
        self.print_header("Testing Search Functionality")
        
        test_queries = [
            ("Normal search", "test"),
            ("Special characters", "<script>alert('xss')</script>"),
            ("SQL injection attempt", "'; DROP TABLE assets; --"),
            ("Long query", "a" * 200),
            ("Empty query", ""),
        ]
        
        for name, query in test_queries:
            try:
                response = self.client.get(f'/marketplace/?q={query}')
                if response.status_code == 200:
                    self.print_success(f"Search handles: {name}")
                else:
                    self.print_error(f"Search {name}", f"Status {response.status_code}")
            except Exception as e:
                self.print_error(f"Search {name}", str(e))
    
    def test_role_system(self):
        """Test role-based access control"""
        self.print_header("Testing Role System")
        
        try:
            # Check if roles are defined
            roles = ['PLAYER', 'CREATOR', 'DEVELOPER', 'RECRUITER', 'MENTOR']
            role_choices = [choice[0] for choice in UserProfile.ROLE_CHOICES]
            
            for role in roles:
                if role in role_choices:
                    self.print_success(f"Role defined: {role}")
                else:
                    self.print_error(f"Role missing: {role}")
                    
        except Exception as e:
            self.print_error("Role system", str(e))
    
    def run_all_tests(self):
        """Run all tests"""
        print(f"\n{Fore.MAGENTA}{'='*60}")
        print(f"{Fore.MAGENTA}Vector Space - Comprehensive System Test")
        print(f"{Fore.MAGENTA}{'='*60}\n")
        
        self.test_security_settings()
        self.test_database_models()
        self.test_file_validators()
        self.test_public_urls()
        self.test_dashboard_urls()
        self.test_api_endpoints()
        self.test_authentication_flow()
        self.test_search_functionality()
        self.test_role_system()
        
        # Print summary
        self.print_header("Test Summary")
        total = self.passed + self.failed
        pass_rate = (self.passed / total * 100) if total > 0 else 0
        
        print(f"{Fore.GREEN}Passed: {self.passed}")
        print(f"{Fore.RED}Failed: {self.failed}")
        print(f"{Fore.CYAN}Total: {total}")
        print(f"{Fore.YELLOW}Pass Rate: {pass_rate:.1f}%\n")
        
        if self.errors:
            print(f"{Fore.RED}Errors Found:")
            for i, (test, error) in enumerate(self.errors, 1):
                print(f"{Fore.RED}{i}. {test}")
                print(f"{Fore.YELLOW}   {error}\n")
        
        if self.failed == 0:
            print(f"{Fore.GREEN}{'='*60}")
            print(f"{Fore.GREEN}✓ ALL TESTS PASSED!")
            print(f"{Fore.GREEN}{'='*60}\n")
        else:
            print(f"{Fore.YELLOW}{'='*60}")
            print(f"{Fore.YELLOW}⚠ SOME TESTS FAILED - Review errors above")
            print(f"{Fore.YELLOW}{'='*60}\n")

if __name__ == '__main__':
    try:
        tester = SystemTester()
        tester.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test interrupted by user")
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error: {e}")
        traceback.print_exc()
