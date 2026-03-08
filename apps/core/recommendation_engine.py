from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from typing import List, Dict
from collections import defaultdict

from apps.users.models import User
from apps.marketplace.models import Asset, Purchase, Review
from apps.games.models import Game, GameReview, FollowDeveloper
from apps.jobs.models import Job, Application, SavedJob
from apps.social.models import Follow
from apps.core.recommendation_models import (
    UserInteraction, UserPreference
)


class BaseRecommendationEngine:
    """
    Base recommendation engine with common scoring algorithms.
    This handles the core logic for content similarity, user behavior analysis,
    social signals, and trending content identification.
    """
    
    def __init__(self, user: User):
        self.user = user
        self.user_prefs = self._get_or_create_preferences()
        
    def _get_or_create_preferences(self) -> UserPreference:
        """Get or create user preferences with defaults based on profile"""
        prefs, created = UserPreference.objects.get_or_create(
            user=self.user,
            defaults={
                'preferred_asset_types': self._infer_asset_preferences(),
                'preferred_game_genres': self._infer_game_preferences(), 
                'preferred_job_types': self._infer_job_preferences(),
                'preferred_software': self._infer_software_preferences(),
            }
        )
        return prefs
    
    def _infer_asset_preferences(self) -> List[str]:
        """Infer asset type preferences from user profile and purchase history"""
        preferences = []
        
        # Based on user type
        if self.user.user_type in ['artist', 'vfx']:
            preferences.extend(['3d_model', 'texture', 'vfx', 'material'])
        elif self.user.user_type == 'developer':
            preferences.extend(['plugin', 'script', 'sound', 'animation'])
            
        # Based on purchase history
        purchased_types = Purchase.objects.filter(buyer=self.user).values_list(
            'asset__asset_type', flat=True
        ).distinct()
        preferences.extend(list(purchased_types))
        
        return list(set(preferences))
    
    def _infer_game_preferences(self) -> List[str]:
        """Infer game genre preferences from downloads and reviews"""
        # Get genres of games user has reviewed/downloaded
        reviewed_genres = GameReview.objects.filter(user=self.user).values_list(
            'game__genre', flat=True
        ).distinct()
        return list(reviewed_genres)
    
    def _infer_job_preferences(self) -> List[str]:
        """Infer job preferences from applications and saved jobs"""
        job_types = set()
        
        # From applications
        applied_types = Application.objects.filter(applicant=self.user).values_list(
            'job__job_type', flat=True
        )
        job_types.update(applied_types)
        
        # From saved jobs
        saved_types = SavedJob.objects.filter(user=self.user).values_list(
            'job__job_type', flat=True
        )
        job_types.update(saved_types)
        
        return list(job_types)
    
    def _infer_software_preferences(self) -> List[str]:
        """Infer software preferences from user skills and purchases"""
        software = []
        
        # From user skills
        if hasattr(self.user, 'skills') and self.user.skills:
            software.extend([skill.lower() for skill in self.user.skills 
                           if skill.lower() in ['blender', 'maya', 'unity', 'unreal']])
        
        # From asset purchases  
        purchased_software = Purchase.objects.filter(buyer=self.user).values_list(
            'asset__software', flat=True
        ).distinct()
        software.extend([s for s in purchased_software if s])
        
        return list(set(software))
    
    def calculate_content_similarity_score(self, content_metadata: Dict, 
                                         content_type: str) -> float:
        """
        Calculate content similarity based on user preferences.
        Returns score from 0.0 to 1.0.
        """
        score = 0.0
        
        if content_type == 'asset':
            # Asset type preference match
            if content_metadata.get('asset_type') in self.user_prefs.preferred_asset_types:
                score += 0.4
                
            # Software compatibility
            if content_metadata.get('software') in self.user_prefs.preferred_software:
                score += 0.3
                
            # Category/tags similarity (simplified - could be improved with NLP)
            user_purchased_categories = set(
                Purchase.objects.filter(buyer=self.user).values_list(
                    'asset__category__name', flat=True
                )
            )
            if content_metadata.get('category') in user_purchased_categories:
                score += 0.2
                
            # Price preference
            max_price = self.user_prefs.max_price_preference
            if max_price and content_metadata.get('price', 0) <= max_price:
                score += 0.1
                
        elif content_type == 'game':
            # Genre preference match
            if content_metadata.get('genre') in self.user_prefs.preferred_game_genres:
                score += 0.5
                
            # Platform preference (assume user prefers PC if they're developers/artists)
            if self.user.user_type in ['developer', 'artist'] and content_metadata.get('platform') == 'pc':
                score += 0.2
                
            # Engine preference
            if content_metadata.get('engine') in self.user_prefs.preferred_software:
                score += 0.3
                
        elif content_type == 'job':
            # Job type preference
            if content_metadata.get('job_type') in self.user_prefs.preferred_job_types:
                score += 0.4
                
            # Skills match
            user_skills = set([skill.lower() for skill in (self.user.skills or [])])
            required_skills = set([skill.lower() for skill in content_metadata.get('required_skills', [])])
            if user_skills.intersection(required_skills):
                score += 0.4
                
            # Location preference (remote friendly)
            if content_metadata.get('remote') and self.user_prefs.preferred_job_types:
                score += 0.2
        
        return min(score, 1.0)
    
    def calculate_user_behavior_score(self, content_id: int, content_type: str) -> float:
        """
        Calculate score based on user's historical behavior patterns.
        Returns score from 0.0 to 1.0.
        """
        score = 0.0
        
        # Recent interaction patterns (last 30 days)
        recent_date = timezone.now() - timedelta(days=30)
        recent_interactions = UserInteraction.objects.filter(
            user=self.user,
            content_type=content_type,
            created_at__gte=recent_date
        )
        
        # User's interaction frequency with this content type
        content_type_interactions = recent_interactions.filter(
            content_type=content_type
        ).count()
        
        if content_type_interactions > 0:
            score += 0.3  # User is active in this content type
            
        # Similar content interaction score
        similar_content_score = self._calculate_similar_content_interaction(
            content_id, content_type
        )
        score += similar_content_score * 0.4
        
        # Recency boost for user's activity patterns
        user_active_hours = self._get_user_active_hours()
        current_hour = timezone.now().hour
        if current_hour in user_active_hours:
            score += 0.1
        
        # Engagement depth score (time spent, multiple views)
        engagement_score = self._calculate_engagement_score(content_id, content_type)
        score += engagement_score * 0.2
        
        return min(score, 1.0)
    
    def _calculate_similar_content_interaction(self, content_id: int, 
                                             content_type: str) -> float:
        """Calculate how much user interacts with similar content"""
        # This is a simplified version - in production, you'd use more sophisticated 
        # similarity analysis (collaborative filtering, content embeddings, etc.)
        
        if content_type == 'asset':
            # Find assets with similar attributes that user has interacted with
            try:
                target_asset = Asset.objects.get(id=content_id)
                similar_interactions = UserInteraction.objects.filter(
                    user=self.user,
                    content_type='asset'
                ).filter(
                    Q(content_id__in=Asset.objects.filter(
                        category=target_asset.category
                    ).values_list('id', flat=True)) |
                    Q(content_id__in=Asset.objects.filter(
                        asset_type=target_asset.asset_type
                    ).values_list('id', flat=True))
                ).count()
                
                # Normalize by total interactions
                total_interactions = UserInteraction.objects.filter(
                    user=self.user, content_type='asset'
                ).count()
                
                return similar_interactions / max(total_interactions, 1) if total_interactions > 0 else 0.0
                
            except Asset.DoesNotExist:
                return 0.0
                
        return 0.0
    
    def _get_user_active_hours(self) -> List[int]:
        """Get hours when user is most active based on interaction history"""
        interactions = UserInteraction.objects.filter(user=self.user)
        hour_counts = defaultdict(int)
        
        for interaction in interactions:
            hour = interaction.created_at.hour
            hour_counts[hour] += 1
        
        if not hour_counts:
            return list(range(9, 18))  # Default business hours
            
        # Return top 50% of active hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        top_hours = sorted_hours[:len(sorted_hours)//2 + 1]
        return [hour for hour, count in top_hours]
    
    def _calculate_engagement_score(self, content_id: int, content_type: str) -> float:
        """Calculate engagement score based on interaction depth"""
        interactions = UserInteraction.objects.filter(
            user=self.user,
            content_id=content_id,
            content_type=content_type
        )
        
        if not interactions.exists():
            return 0.0
        
        score = 0.0
        
        # Multiple views indicate interest
        view_count = interactions.filter(interaction_type='view').count()
        if view_count > 1:
            score += 0.3
        
        # Time spent (if available)
        avg_duration = interactions.filter(
            duration_seconds__isnull=False
        ).aggregate(Avg('duration_seconds'))['duration_seconds__avg']
        
        if avg_duration and avg_duration > 30:  # More than 30 seconds
            score += 0.4
            
        # High-value interactions
        high_value_interactions = interactions.filter(
            interaction_type__in=['purchase', 'like', 'download']
        ).count()
        
        if high_value_interactions > 0:
            score += 0.3
            
        return min(score, 1.0)
    
    def calculate_social_signals_score(self, content_id: int, content_type: str) -> float:
        """
        Calculate score based on social signals from user's network.
        Returns score from 0.0 to 1.0.
        """
        if not self.user_prefs.include_social_signals:
            return 0.0
            
        score = 0.0
        
        # Get users that this user follows
        following_users = Follow.objects.filter(
            follower=self.user
        ).values_list('following_id', flat=True)
        
        if not following_users:
            return 0.0
        
        # Check interactions from followed users with this content
        following_interactions = UserInteraction.objects.filter(
            user_id__in=following_users,
            content_id=content_id,
            content_type=content_type
        )
        
        # Different interaction types have different weights
        interaction_weights = {
            'purchase': 0.4,
            'like': 0.2,
            'download': 0.3,
            'view': 0.1,
        }
        
        for interaction in following_interactions:
            weight = interaction_weights.get(interaction.interaction_type, 0.1)
            score += weight
        
        # Boost for highly rated content by followed users
        if content_type in ['asset', 'game']:
            following_reviews = None
            if content_type == 'asset':
                following_reviews = Review.objects.filter(
                    user_id__in=following_users,
                    asset_id=content_id,
                    rating__gte=4
                )
            elif content_type == 'game':
                following_reviews = GameReview.objects.filter(
                    user_id__in=following_users,
                    game_id=content_id,
                    rating__gte=4
                )
            
            if following_reviews and following_reviews.exists():
                score += 0.3
        
        # Developer following bonus for games
        if content_type == 'game':
            try:
                game = Game.objects.get(id=content_id)
                if FollowDeveloper.objects.filter(
                    follower=self.user,
                    developer=game.developer
                ).exists():
                    score += 0.2
            except Game.DoesNotExist:
                pass
        
        return min(score, 1.0)
    
    def calculate_trending_score(self, content_id: int, content_type: str) -> float:
        """
        Calculate trending score based on recent activity.
        Returns score from 0.0 to 1.0.
        """
        if not self.user_prefs.include_trending:
            return 0.0
        
        score = 0.0
        recent_date = timezone.now() - timedelta(days=7)  # Last 7 days
        
        # Recent interactions count
        recent_interactions = UserInteraction.objects.filter(
            content_id=content_id,
            content_type=content_type, 
            created_at__gte=recent_date
        ).count()
        
        # Get average interactions for this content type in same period
        avg_interactions = UserInteraction.objects.filter(
            content_type=content_type,
            created_at__gte=recent_date
        ).values('content_id').annotate(
            interaction_count=Count('id')
        ).aggregate(Avg('interaction_count'))['interaction_count__avg'] or 1
        
        # Trending multiplier
        trending_multiplier = recent_interactions / avg_interactions
        
        if trending_multiplier > 1.5:
            score += 0.4  # Significantly above average
        elif trending_multiplier > 1.2:
            score += 0.2  # Above average
        
        # New content boost (published in last 30 days)
        content_age_score = self._calculate_content_age_score(content_id, content_type)
        score += content_age_score * 0.3
        
        # Featured content boost
        featured_boost = self._get_featured_boost(content_id, content_type)
        score += featured_boost * 0.3
        
        return min(score, 1.0)
    
    def _calculate_content_age_score(self, content_id: int, content_type: str) -> float:
        """Give boost to newer content"""
        try:
            content_date = None
            if content_type == 'asset':
                content_date = Asset.objects.get(id=content_id).created_at
            elif content_type == 'game':
                content_date = Game.objects.get(id=content_id).created_at
            elif content_type == 'job':
                content_date = Job.objects.get(id=content_id).created_at
            
            if not content_date:
                return 0.0
            
            days_old = (timezone.now() - content_date).days
            
            if days_old <= 7:
                return 1.0  # Very new
            elif days_old <= 30:
                return 0.7  # Recent
            elif days_old <= 90:
                return 0.3  # Somewhat recent
            else:
                return 0.0  # Old
                
        except Exception:
            return 0.0
    
    def _get_featured_boost(self, content_id: int, content_type: str) -> float:
        """Check if content is featured"""
        try:
            if content_type == 'asset':
                asset = Asset.objects.get(id=content_id)
                return 1.0 if asset.featured else 0.0
            # Add similar logic for games and jobs if they have featured flags
        except Exception:
            pass
        return 0.0