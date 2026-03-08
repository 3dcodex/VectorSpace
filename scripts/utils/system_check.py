"""
Vector Space - Comprehensive System Check
Validates all routes, pages, and functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import get_resolver, URLPattern, URLResolver
from django.test import Client
from django.contrib.auth import get_user_model
from colorama import init, Fore
import time

init(autoreset=True)

User = get_user_model()


class SystemChecker:
    def __init__(self):
        self.client = Client()
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
        self.test_user = None
        
    def setup_test_user(self):
        """Create a test user for authenticated routes"""
        try:
            self.test_user = User.objects.create_user(
                username='systemcheck_user',
                email='systemcheck@test.com',
                password='testpass123'
            )
            print(f"{Fore.GREEN}✓ Test user created")
        except Exception:
            print(f"{Fore.YELLOW}⚠ Using existing test user")
            self.test_user = User.objects.filter(username='systemcheck_user').first()
    
    def cleanup_test_user(self):
        """Remove test user after checks"""
        if self.test_user:
            self.test_user.delete()
            print(f"{Fore.GREEN}✓ Test user cleaned up")
    
    def get_all_urls(self, urlpatterns=None, prefix=''):
        """Recursively get all URL patterns"""
        if urlpatterns is None:
            urlpatterns = get_resolver().url_patterns
        
        urls = []
        for pattern in urlpatterns:
            if isinstance(pattern, URLResolver):
                urls.extend(self.get_all_urls(pattern.url_patterns, prefix + str(pattern.pattern)))
            elif isinstance(pattern, URLPattern):
                url = prefix + str(pattern.pattern)
                # Clean up the URL
                url = url.replace('^', '').replace('$', '')
                if '<' not in url and url:  # Skip parameterized URLs for now
                    urls.append(url)
        return urls
    
    def check_public_routes(self):
        """Check all public routes"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}CHECKING PUBLIC ROUTES")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        public_routes = [
            ('/', 'Home Page'),
            ('/marketplace/', 'Marketplace List'),
            ('/games/', 'Games List'),
            ('/jobs/', 'Jobs List'),
            ('/community/', 'Community Page'),
            ('/competitions/', 'Competitions List'),
            ('/mentorship/', 'Mentorship List'),
            ('/auth/login/', 'Login Page'),
            ('/auth/signup/', 'Signup Page'),
        ]
        
        for route, name in public_routes:
            try:
                start_time = time.time()
                response = self.client.get(route)
                load_time = time.time() - start_time
                
                if response.status_code == 200:
                    status = f"{Fore.GREEN}✓ PASS"
                    self.results['passed'].append(f"{name} ({route})")
                    
                    # Check load time
                    if load_time > 2.0:
                        self.results['warnings'].append(f"{name} slow load time: {load_time:.2f}s")
                        print(f"{status} {name:30} {Fore.YELLOW}⚠ Slow: {load_time:.2f}s")
                    else:
                        print(f"{status} {name:30} {Fore.GREEN}{load_time:.2f}s")
                else:
                    status = f"{Fore.RED}✗ FAIL"
                    self.results['failed'].append(f"{name} ({route}) - Status: {response.status_code}")
                    print(f"{status} {name:30} Status: {response.status_code}")
            except Exception as e:
                self.results['failed'].append(f"{name} ({route}) - Error: {str(e)}")
                print(f"{Fore.RED}✗ FAIL {name:30} Error: {str(e)}")
    
    def check_authenticated_routes(self):
        """Check routes that require authentication"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}CHECKING AUTHENTICATED ROUTES")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        # Login first
        self.client.login(username='systemcheck_user', password='testpass123')
        
        auth_routes = [
            ('/dashboard/', 'Dashboard Overview'),
            ('/dashboard/marketplace/', 'Marketplace Dashboard'),
            ('/dashboard/games/', 'Games Dashboard'),
            ('/dashboard/social/feed/', 'Social Feed'),
            ('/dashboard/jobs/', 'Jobs Dashboard'),
            ('/dashboard/competitions/', 'Competitions Dashboard'),
            ('/dashboard/mentorship/', 'Mentorship Dashboard'),
            ('/dashboard/analytics/', 'Analytics Dashboard'),
            ('/notifications/', 'Notifications'),
        ]
        
        for route, name in auth_routes:
            try:
                start_time = time.time()
                response = self.client.get(route)
                load_time = time.time() - start_time
                
                if response.status_code == 200:
                    status = f"{Fore.GREEN}✓ PASS"
                    self.results['passed'].append(f"{name} ({route})")
                    print(f"{status} {name:30} {Fore.GREEN}{load_time:.2f}s")
                elif response.status_code == 302:
                    status = f"{Fore.YELLOW}⚠ REDIRECT"
                    self.results['warnings'].append(f"{name} ({route}) - Redirected")
                    print(f"{status} {name:30} Redirected")
                else:
                    status = f"{Fore.RED}✗ FAIL"
                    self.results['failed'].append(f"{name} ({route}) - Status: {response.status_code}")
                    print(f"{status} {name:30} Status: {response.status_code}")
            except Exception as e:
                self.results['failed'].append(f"{name} ({route}) - Error: {str(e)}")
                print(f"{Fore.RED}✗ FAIL {name:30} Error: {str(e)}")
        
        # Logout
        self.client.logout()
    
    def check_static_files(self):
        """Check if static files are accessible"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}CHECKING STATIC FILES")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        static_files = [
            '/static/css/style.css',
            '/static/css/dashboard.css',
            '/static/js/main.js',
            '/static/images/logo.png',
        ]
        
        for file_path in static_files:
            try:
                response = self.client.get(file_path)
                if response.status_code == 200:
                    print(f"{Fore.GREEN}✓ PASS {file_path}")
                    self.results['passed'].append(f"Static file: {file_path}")
                else:
                    print(f"{Fore.YELLOW}⚠ WARN {file_path} - Status: {response.status_code}")
                    self.results['warnings'].append(f"Static file {file_path} - Status: {response.status_code}")
            except Exception as e:
                print(f"{Fore.RED}✗ FAIL {file_path} - Error: {str(e)}")
                self.results['warnings'].append(f"Static file {file_path} - Error: {str(e)}")
    
    def check_ui_components(self):
        """Check if UI components are present"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}CHECKING UI COMPONENTS")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        response = self.client.get('/')
        content = response.content.decode('utf-8')
        
        components = [
            ('main-header', 'Header'),
            ('header-nav', 'Navigation'),
            ('main-footer', 'Footer'),
            ('mobile-menu', 'Mobile Menu'),
            ('user-menu', 'User Menu (if logged in)'),
        ]
        
        for component_class, component_name in components:
            if component_class in content:
                print(f"{Fore.GREEN}✓ PASS {component_name}")
                self.results['passed'].append(f"UI Component: {component_name}")
            else:
                print(f"{Fore.YELLOW}⚠ WARN {component_name} not found")
                self.results['warnings'].append(f"UI Component {component_name} not found")
    
    def check_database_connectivity(self):
        """Check database connectivity"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}CHECKING DATABASE")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            print(f"{Fore.GREEN}✓ PASS Database connection")
            self.results['passed'].append("Database connection")
        except Exception as e:
            print(f"{Fore.RED}✗ FAIL Database connection - Error: {str(e)}")
            self.results['failed'].append(f"Database connection - Error: {str(e)}")
    
    def check_models(self):
        """Check if models are properly configured"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}CHECKING MODELS")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        models_to_check = [
            ('apps.marketplace.models', 'Asset'),
            ('apps.games.models', 'Game'),
            ('apps.jobs.models', 'Job'),
            ('apps.social.models', 'Post'),
            ('apps.competitions.models', 'Competition'),
            ('apps.mentorship.models', 'MentorProfile'),
        ]
        
        for module_path, model_name in models_to_check:
            try:
                module = __import__(module_path, fromlist=[model_name])
                model = getattr(module, model_name)
                count = model.objects.count()
                print(f"{Fore.GREEN}✓ PASS {model_name:20} ({count} records)")
                self.results['passed'].append(f"Model: {model_name}")
            except Exception as e:
                print(f"{Fore.RED}✗ FAIL {model_name:20} Error: {str(e)}")
                self.results['failed'].append(f"Model {model_name} - Error: {str(e)}")
    
    def generate_report(self):
        """Generate final report"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}SYSTEM CHECK REPORT")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        total_tests = len(self.results['passed']) + len(self.results['failed']) + len(self.results['warnings'])
        pass_rate = (len(self.results['passed']) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"{Fore.GREEN}✓ Passed: {len(self.results['passed'])}")
        print(f"{Fore.RED}✗ Failed: {len(self.results['failed'])}")
        print(f"{Fore.YELLOW}⚠ Warnings: {len(self.results['warnings'])}")
        print(f"\n{Fore.CYAN}Pass Rate: {pass_rate:.1f}%\n")
        
        if self.results['failed']:
            print(f"{Fore.RED}FAILED TESTS:")
            for failure in self.results['failed']:
                print(f"  {Fore.RED}✗ {failure}")
        
        if self.results['warnings']:
            print(f"\n{Fore.YELLOW}WARNINGS:")
            for warning in self.results['warnings']:
                print(f"  {Fore.YELLOW}⚠ {warning}")
        
        print(f"\n{Fore.CYAN}{'='*60}")
        if len(self.results['failed']) == 0:
            print(f"{Fore.GREEN}✓ ALL CRITICAL TESTS PASSED!")
        else:
            print(f"{Fore.RED}✗ SOME TESTS FAILED - REVIEW REQUIRED")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        return len(self.results['failed']) == 0
    
    def run_all_checks(self):
        """Run all system checks"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}VECTOR SPACE - SYSTEM CHECK")
        print(f"{Fore.CYAN}{'='*60}\n")
        
        start_time = time.time()
        
        self.setup_test_user()
        self.check_database_connectivity()
        self.check_models()
        self.check_public_routes()
        self.check_authenticated_routes()
        self.check_static_files()
        self.check_ui_components()
        self.cleanup_test_user()
        
        total_time = time.time() - start_time
        print(f"\n{Fore.CYAN}Total check time: {total_time:.2f}s")
        
        return self.generate_report()


def main():
    """Main entry point"""
    checker = SystemChecker()
    success = checker.run_all_checks()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
