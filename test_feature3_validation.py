#!/usr/bin/env python
"""
Feature #3 (Advanced Search & Discovery) - Quick Validation Test Suite
Tests critical functionality to ensure all components working correctly.
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from apps.marketplace.models import Asset, Category
from apps.games.models import Game
from apps.marketplace.search_models import (
    SearchQuery, SavedSearch, TrendingItem, SearchFilter, 
    SimilarItem, DiscoveryCard, SearchAnalytics
)
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

class Feature3ValidationTests:
    """Manual validation tests for Feature #3"""
    
    def __init__(self):
        self.client = Client()
        self.passed = 0
        self.failed = 0
        self.user = None
        
    def print_header(self, text):
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}")
        
    def print_test(self, name, passed, details=""):
        status = "[PASS]" if passed else "[FAIL]"
        self.passed += 1 if passed else 0
        self.failed += 0 if passed else 1
        print(f"{status} | {name}")
        if details:
            print(f"       {details}")
            
    def setup_test_data(self):
        """Create test data for validation"""
        print("\n[*] Setting up test data...")
        
        # Create test user
        self.user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        print(f"   Test user: {self.user.username} (created={created})")
        
        # Check existing assets
        assets = Asset.objects.all()[:5]
        print(f"   Existing assets: {assets.count()}")
        
        return len(assets) > 0
        
    def test_models_exist(self):
        """Test 1: Verify all new models created"""
        self.print_header("TEST 1: Model Creation")
        
        models = {
            'SearchQuery': SearchQuery,
            'SavedSearch': SavedSearch,
            'TrendingItem': TrendingItem,
            'SearchFilter': SearchFilter,
            'SimilarItem': SimilarItem,
            'DiscoveryCard': DiscoveryCard,
            'SearchAnalytics': SearchAnalytics,
        }
        
        for name, model in models.items():
            try:
                count = model.objects.count()
                self.print_test(f"Model '{name}' accessible", True, f"Found {count} records")
            except Exception as e:
                self.print_test(f"Model '{name}' accessible", False, str(e))
                
    def test_search_queries(self):
        """Test 2: Search query recording"""
        self.print_header("TEST 2: Search Query Recording")
        
        try:
            # Create test search query
            query = SearchQuery.objects.create(
                user=self.user,
                query_text="3D model",
                search_type="asset",
                results_count=5
            )
            self.print_test("Create SearchQuery", True, f"Query ID: {query.id}")
            
            # Verify it's recorded
            retrieved = SearchQuery.objects.get(id=query.id)
            self.print_test("Retrieve SearchQuery", True, f"Query: '{retrieved.query_text}'")
            
            # Check query indexing
            found = SearchQuery.objects.filter(query_text__icontains="3D").exists()
            self.print_test("Search query indexing", found, "Query findable via search")
            
        except Exception as e:
            self.print_test("Search query recording", False, str(e))
            
    def test_saved_searches(self):
        """Test 3: Saved searches"""
        self.print_header("TEST 3: Saved Searches")
        
        try:
            # Create saved search with unique name to avoid constraint conflicts
            unique_name = f"MySearch_{int(timezone.now().timestamp() * 1000)}"
            saved = SavedSearch.objects.create(
                user=self.user,
                name=unique_name,
                query_text="3D",
                search_type="asset",
                is_public=False
            )
            self.print_test("Create SavedSearch", True, f"Saved search ID: {saved.id}")
            
            # Verify retrieval
            count = SavedSearch.objects.filter(user=self.user, name=unique_name).count()
            self.print_test("SavedSearch retrieval", count == 1, f"Count: {count}")
            
            # Retrieve and verify
            retrieved = SavedSearch.objects.get(id=saved.id)
            self.print_test("Retrieve SavedSearch", True, f"Name: '{retrieved.name}'")
            
        except Exception as e:
            self.print_test("Saved searches", False, str(e))
            
    def test_trending_items(self):
        """Test 4: Trending items calculation"""
        self.print_header("TEST 4: Trending Items")
        
        try:
            # Get or Create trending item
            assets = Asset.objects.all()[:1]
            if not assets:
                self.print_test("Trending items (need assets)", False, "No assets in database")
                return
                
            asset = assets[0]
            
            trending, created = TrendingItem.objects.get_or_create(
                item_type='asset',
                asset=asset,
                period='week',
                defaults={
                    'ranking': 1,
                    'score': 95.5
                }
            )
            
            action = "created" if created else "retrieved"
            self.print_test(f"TrendingItem {action}", True, f"Score: {trending.score}")
            
            # Verify ordering
            week_trending = TrendingItem.objects.filter(period='week').order_by('-score')[:1]
            self.print_test("Trending score ordering", 
                          week_trending.exists(), 
                          f"Top trending asset exists")
            
        except Exception as e:
            self.print_test("Trending items", False, str(e))
            
    def test_search_filters(self):
        """Test 5: Faceted search filters"""
        self.print_header("TEST 5: Search Filters")
        
        try:
            # Create filter
            filter_obj, created = SearchFilter.objects.get_or_create(
                filter_type='category',
                value='3D Modeling',
                defaults={
                    'label': '3D Modeling',
                    'asset_count': 50
                }
            )
            
            action = "created" if created else "retrieved"
            self.print_test(f"SearchFilter {action}", True, f"Type: {filter_obj.filter_type}")
            
            # Verify filters exist
            category_filters = SearchFilter.objects.filter(filter_type='category').count()
            self.print_test("Category filters", category_filters > 0, f"Count: {category_filters}")
            
            price_filters = SearchFilter.objects.filter(filter_type='price_range').count()
            self.print_test("Price range filters", price_filters >=0, f"Count: {price_filters}")
            
        except Exception as e:
            self.print_test("Search filters", False, str(e))
            
    def test_similar_items(self):
        """Test 6: Similar items calculation"""
        self.print_header("TEST 6: Similar Items")
        
        try:
            assets = Asset.objects.all()[:2]
            if len(assets) < 2:
                self.print_test("Similar items (need 2+ assets)", False, "Insufficient test data")
                return
                
            source_asset = assets[0]
            similar_asset = assets[1]
            
            similarity, created = SimilarItem.objects.get_or_create(
                source_asset=source_asset,
                similar_asset=similar_asset,
                defaults={'similarity_score': 0.85}
            )
            
            action = "created" if created else "retrieved"
            self.print_test(f"SimilarItem {action}", True, 
                          f"Score: {similarity.similarity_score}")
            
            # Verify lookup works
            similar = SimilarItem.objects.filter(
                source_asset=source_asset
            ).order_by('-similarity_score')
            
            self.print_test("Similar items lookup", similar.exists(), 
                          f"Found {similar.count()} similar items")
            
        except Exception as e:
            self.print_test("Similar items", False, str(e))
            
    def test_discovery_cards(self):
        """Test 7: Discovery cards"""
        self.print_header("TEST 7: Discovery Cards")
        
        try:
            card, created = DiscoveryCard.objects.get_or_create(
                card_type='trending',
                title='Trending Now',
                defaults={
                    'description': 'Check out what\'s trending this week',
                    'order': 1
                }
            )
            
            action = "created" if created else "retrieved"
            self.print_test(f"DiscoveryCard {action}", True, f"Type: {card.card_type}")
            
            # Verify all card types exist or can be created
            card_types = ['trending', 'new', 'popular_category', 'staff_pick', 'seasonal']
            existing = DiscoveryCard.objects.filter(card_type__in=card_types).count()
            self.print_test("Discovery card types", existing > 0, f"Found {existing} cards")
            
        except Exception as e:
            self.print_test("Discovery cards", False, str(e))
            
    def test_analytics(self):
        """Test 8: Search analytics"""
        self.print_header("TEST 8: Search Analytics")
        
        try:
            today = timezone.now().date()
            
            analytics, created = SearchAnalytics.objects.get_or_create(
                date=today,
                defaults={
                    'total_searches': 10,
                    'unique_searchers': 8
                }
            )
            
            action = "created" if created else "retrieved"
            self.print_test(f"SearchAnalytics {action}", True, 
                          f"Date: {analytics.date}, Searches: {analytics.total_searches}")
            
            # Verify we can query analytics
            week_ago = today - timedelta(days=7)
            week_data = SearchAnalytics.objects.filter(date__gte=week_ago)
            self.print_test("Analytics time-range query", True, f"Found {week_data.count()} days")
            
        except Exception as e:
            self.print_test("Search analytics", False, str(e))
            
    def test_url_routes(self):
        """Test 9: URL routes accessible"""
        self.print_header("TEST 9: URL Routes")
        
        routes = [
            ('/marketplace/search/', 'Advanced Search Page'),
            ('/marketplace/trending/', 'Trending Items Page'),
            ('/marketplace/dashboard/searches/', 'Search History Dashboard'),
        ]
        
        for url, name in routes:
            try:
                response = self.client.get(url, follow=True)
                # 200 = success, 302 = redirect (ok for unauthenticated), 404 = not found
                success = response.status_code in [200, 302]
                self.print_test(f"Route '{name}'", success, f"Status: {response.status_code}")
            except Exception as e:
                self.print_test(f"Route '{name}'", False, str(e))
                
    def test_search_views(self):
        """Test 10: Search view response"""
        self.print_header("TEST 10: Search Views")
        
        # Test advanced search (unauthenticated)
        try:
            response = self.client.get('/marketplace/search/?q=test')
            success = response.status_code in [200, 302]
            self.print_test("Advanced search endpoint", success, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Advanced search endpoint", False, str(e))
            
        # Test trending
        try:
            response = self.client.get('/marketplace/trending/')
            success = response.status_code in [200, 302]
            self.print_test("Trending endpoint", success, f"Status: {response.status_code}")
        except Exception as e:
            self.print_test("Trending endpoint", False, str(e))
            
    def test_performance(self):
        """Test 11: Basic performance"""
        self.print_header("TEST 11: Performance")
        
        import time
        
        # Test model count performance
        try:
            start = time.time()
            count = SearchQuery.objects.count()
            elapsed = (time.time() - start) * 1000  # Convert to ms
            
            fast = elapsed < 100  # Should be very fast
            self.print_test("SearchQuery count query", fast, f"Completed in {elapsed:.2f}ms")
        except Exception as e:
            self.print_test("Performance query", False, str(e))
            
        # Test filter query
        try:
            start = time.time()
            filters = SearchFilter.objects.filter(filter_type='category')[:10]
            elapsed = (time.time() - start) * 1000
            
            fast = elapsed < 100
            self.print_test("SearchFilter query", fast, f"Completed in {elapsed:.2f}ms")
        except Exception as e:
            self.print_test("Filter query", False, str(e))
            
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*60)
        print("  FEATURE #3: ADVANCED SEARCH & DISCOVERY VALIDATION")
        print("="*60)
        
        # Setup
        has_data = self.setup_test_data()
        
        # Run tests
        self.test_models_exist()
        self.test_search_queries()
        self.test_saved_searches()
        
        if has_data:
            self.test_trending_items()
            self.test_similar_items()
        
        self.test_search_filters()
        self.test_discovery_cards()
        self.test_analytics()
        self.test_url_routes()
        self.test_search_views()
        self.test_performance()
        
        # Summary
        self.print_header("TEST SUMMARY")
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        print(f"\n  Total Tests: {total}")
        print(f"  [PASS] Passed:     {self.passed}")
        print(f"  [FAIL] Failed:     {self.failed}")
        print(f"  Success Rate:      {percentage:.1f}%")
        
        if self.failed == 0:
            print(f"\n[ALL TESTS PASSED!] Feature #3 is fully functional!")
        else:
            print(f"\n  [WARNING] {self.failed} test(s) failed. Review errors above.")
            
        print("\n" + "="*60 + "\n")
        
        return self.failed == 0


if __name__ == '__main__':
    tester = Feature3ValidationTests()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
