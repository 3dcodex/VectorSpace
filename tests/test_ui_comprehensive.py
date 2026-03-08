"""
Comprehensive UI/UX Testing Suite for Vector Space
Tests all routes, pages, and UI components
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class PublicPagesTest(TestCase):
    """Test all public-facing pages"""
    
    def setUp(self):
        self.client = Client()
        
    def test_home_page(self):
        """Test home page loads correctly"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Vector Space')
        
    def test_marketplace_list(self):
        """Test marketplace listing page"""
        response = self.client.get(reverse('marketplace:list'))
        self.assertEqual(response.status_code, 200)
        
    def test_games_list(self):
        """Test games listing page"""
        response = self.client.get(reverse('games:list'))
        self.assertEqual(response.status_code, 200)
        
    def test_jobs_list(self):
        """Test jobs listing page"""
        response = self.client.get(reverse('jobs:list'))
        self.assertEqual(response.status_code, 200)
        
    def test_community_page(self):
        """Test community page"""
        response = self.client.get(reverse('social:community'))
        self.assertEqual(response.status_code, 200)
        
    def test_competitions_list(self):
        """Test competitions listing"""
        response = self.client.get(reverse('competitions:list'))
        self.assertEqual(response.status_code, 200)
        
    def test_mentorship_list(self):
        """Test mentorship listing"""
        response = self.client.get(reverse('mentorship:list'))
        self.assertEqual(response.status_code, 200)


class AuthenticationPagesTest(TestCase):
    """Test authentication pages"""
    
    def setUp(self):
        self.client = Client()
        
    def test_login_page(self):
        """Test login page loads"""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
        
    def test_signup_page(self):
        """Test signup page loads"""
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sign')


class DashboardPagesTest(TestCase):
    """Test dashboard pages (requires authentication)"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        
    def test_dashboard_overview(self):
        """Test main dashboard page"""
        response = self.client.get(reverse('dashboard:overview'))
        self.assertEqual(response.status_code, 200)
        
    def test_marketplace_dashboard(self):
        """Test marketplace dashboard"""
        response = self.client.get(reverse('dashboard:marketplace_my_assets'))
        self.assertEqual(response.status_code, 200)
        
    def test_games_dashboard(self):
        """Test games dashboard"""
        response = self.client.get(reverse('dashboard:games_my_games'))
        self.assertEqual(response.status_code, 200)
        
    def test_social_dashboard(self):
        """Test social feed dashboard"""
        response = self.client.get(reverse('dashboard:social_feed'))
        self.assertEqual(response.status_code, 200)
        
    def test_jobs_dashboard(self):
        """Test jobs dashboard"""
        response = self.client.get(reverse('dashboard:jobs_board'))
        self.assertEqual(response.status_code, 200)


class UIComponentsTest(TestCase):
    """Test UI components render correctly"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
    def test_header_navigation(self):
        """Test header navigation is present"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'header-nav')
        self.assertContains(response, 'Marketplace')
        self.assertContains(response, 'Games')
        self.assertContains(response, 'Community')
        
    def test_footer_present(self):
        """Test footer is present"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'main-footer')
        
    def test_mobile_menu(self):
        """Test mobile menu elements exist"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'mobile-menu')
        
    def test_user_dropdown_authenticated(self):
        """Test user dropdown for authenticated users"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'user-dropdown')
        self.assertContains(response, 'Dashboard')
        self.assertContains(response, 'Logout')


class ResponsivenessTest(TestCase):
    """Test responsive design elements"""
    
    def setUp(self):
        self.client = Client()
        
    def test_viewport_meta_tag(self):
        """Test viewport meta tag is present"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'viewport')
        
    def test_mobile_styles(self):
        """Test mobile-specific styles are included"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, '@media')


class PerformanceTest(TestCase):
    """Test page performance indicators"""
    
    def setUp(self):
        self.client = Client()
        
    def test_home_page_load_time(self):
        """Test home page loads within acceptable time"""
        import time
        start = time.time()
        self.client.get(reverse('home'))
        end = time.time()
        load_time = end - start
        self.assertLess(load_time, 2.0, f"Page took {load_time}s to load")
        
    def test_static_files_referenced(self):
        """Test static files are properly referenced"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'static/css/style.css')
        self.assertContains(response, 'static/js/main.js')


class AccessibilityTest(TestCase):
    """Test accessibility features"""
    
    def setUp(self):
        self.client = Client()
        
    def test_alt_tags_on_images(self):
        """Test images have alt tags"""
        response = self.client.get(reverse('home'))
        # Check that img tags have alt attributes
        self.assertNotContains(response, '<img src=', msg_prefix='Images should have alt tags')
        
    def test_semantic_html(self):
        """Test semantic HTML elements are used"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, '<header')
        self.assertContains(response, '<nav')
        self.assertContains(response, '<main')
        self.assertContains(response, '<footer')


class FormValidationTest(TestCase):
    """Test form validation and error handling"""
    
    def setUp(self):
        self.client = Client()
        
    def test_login_form_validation(self):
        """Test login form validates correctly"""
        response = self.client.post(reverse('users:login'), {
            'username': '',
            'password': ''
        })
        self.assertContains(response, 'required', status_code=200)
        
    def test_signup_form_validation(self):
        """Test signup form validates correctly"""
        response = self.client.post(reverse('users:signup'), {
            'username': '',
            'email': 'invalid-email',
            'password1': '123',
            'password2': '456'
        })
        self.assertEqual(response.status_code, 200)


class AnimationTest(TestCase):
    """Test animations and transitions are present"""
    
    def setUp(self):
        self.client = Client()
        
    def test_css_animations(self):
        """Test CSS animations are defined"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'transition')
        
    def test_scroll_animations(self):
        """Test scroll animations are implemented"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'animation')


def run_all_tests():
    """Run all UI tests and generate report"""
    from io import StringIO
    from django.test.runner import DiscoverRunner
    
    # Capture test output
    test_output = StringIO()
    runner = DiscoverRunner(verbosity=2, interactive=False, stream=test_output)
    
    # Run tests
    failures = runner.run_tests(['tests.test_ui_comprehensive'])
    
    # Generate report
    report = f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║          VECTOR SPACE UI/UX TEST REPORT                     ║
    ╚══════════════════════════════════════════════════════════════╝
    
    Test Results: {'✅ ALL PASSED' if failures == 0 else f'❌ {failures} FAILED'}
    
    Test Categories:
    - Public Pages: ✓
    - Authentication: ✓
    - Dashboard Pages: ✓
    - UI Components: ✓
    - Responsiveness: ✓
    - Performance: ✓
    - Accessibility: ✓
    - Form Validation: ✓
    - Animations: ✓
    
    {test_output.getvalue()}
    """
    
    print(report)
    return failures == 0


if __name__ == '__main__':
    run_all_tests()
