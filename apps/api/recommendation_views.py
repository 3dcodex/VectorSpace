from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.core.cache import cache
from django.db.models import F
import logging
from typing import Dict, List

from apps.core.recommendation_services import (
    MarketplaceRecommendations, get_user_recommendations
)
from apps.core.recommendation_models import UserInteraction, UserPreference
from apps.marketplace.models import Asset
from apps.games.models import Game
from apps.jobs.models import Job

logger = logging.getLogger(__name__)


class RecommendationsAPIView(APIView):
    """
    Main recommendations endpoint that supports multiple content types.
    GET /api/recommendations/?type=asset&limit=10
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get personalized recommendations for the authenticated user"""
        try:
            content_type = request.GET.get('type', 'asset')
            limit = min(int(request.GET.get('limit', 10)), 50)  # Max 50 items
            
            # Validate content type
            if content_type not in ['asset', 'game', 'job']:
                return Response({
                    'error': 'Invalid content type. Must be: asset, game, or job'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check cache first (cache for 1 hour per user per content type)
            cache_key = f"recommendations_{request.user.id}_{content_type}_{limit}"
            cached_result = cache.get(cache_key)
            
            if cached_result:
                return Response({
                    'recommendations': cached_result,
                    'content_type': content_type, 
                    'cached': True
                })
            
            # Get fresh recommendations
            recommendations = get_user_recommendations(
                user=request.user,
                content_type=content_type,
                limit=limit
            )
            
            # Serialize for API response
            serialized_recommendations = self._serialize_recommendations(recommendations, content_type)
            
            # Cache the result
            cache.set(cache_key, serialized_recommendations, timeout=3600)  # 1 hour
            
            return Response({
                'recommendations': serialized_recommendations,
                'content_type': content_type,
                'cached': False
            })
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error in recommendations API for user {request.user.id}: {e}")
            return Response({
                'error': 'Failed to generate recommendations'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _serialize_recommendations(self, recommendations: List[Dict], content_type: str) -> List[Dict]:
        """Convert recommendation objects to API-friendly format"""
        serialized = []
        
        for rec in recommendations:
            if content_type == 'asset':
                asset = rec['asset']
                item_data = {
                    'id': asset.id,
                    'title': asset.title,
                    'description': asset.description[:200] + '...' if len(asset.description) > 200 else asset.description,
                    'price': str(asset.price),
                    'asset_type': asset.asset_type,
                    'category': asset.category.name if asset.category else None,
                    'seller': asset.seller.username,
                    'rating': asset.rating,
                    'downloads': asset.downloads,
                    'view_count': asset.view_count,
                    'preview_image': asset.preview_image,
                    'is_free': asset.is_free,
                    'created_at': asset.created_at.isoformat(),
                }
            
            elif content_type == 'game':
                game = rec['game']
                item_data = {
                    'id': game.id,
                    'title': game.title,
                    'description': game.description[:200] + '...' if len(game.description) > 200 else game.description,
                    'genre': game.genre,
                    'platform': game.platform,
                    'engine': game.engine,
                    'developer': game.developer.username,
                    'rating': game.rating,
                    'downloads': game.downloads,
                    'view_count': game.view_count,
                    'thumbnail': game.thumbnail,
                    'verified': game.verified,
                    'created_at': game.created_at.isoformat(),
                }
            
            elif content_type == 'job':
                job = rec['job']
                item_data = {
                    'id': job.id,
                    'title': job.title,
                    'description': job.description[:200] + '...' if len(job.description) > 200 else job.description,
                    'company_name': job.company_name,
                    'job_type': job.job_type,
                    'location': job.location,
                    'remote': job.remote,
                    'experience_level': job.experience_level,
                    'required_skills': job.required_skills,
                    'salary_min': str(job.salary_min) if job.salary_min else None,
                    'salary_max': str(job.salary_max) if job.salary_max else None,
                    'recruiter': job.recruiter.username,
                    'view_count': job.view_count,
                    'created_at': job.created_at.isoformat(),
                }
            
            serialized.append({
                'item': item_data,
                'score': rec['score'],
                'reason': rec['reason'],
                'content_type': content_type
            })
        
        return serialized


class TrackInteractionAPIView(APIView):
    """Track user interactions for recommendation learning"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Record a user interaction"""
        try:
            interaction_type = request.data.get('interaction_type')
            content_type = request.data.get('content_type')
            content_id = request.data.get('content_id')
            duration_seconds = request.data.get('duration_seconds')
            search_query = request.data.get('search_query', '')
            referrer_type = request.data.get('referrer_type', '')
            
            # Validate required fields
            if not all([interaction_type, content_type, content_id]):
                return Response({
                    'error': 'Missing required fields: interaction_type, content_type, content_id'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate choices
            valid_interactions = [choice[0] for choice in UserInteraction.INTERACTION_TYPES]
            valid_content_types = [choice[0] for choice in UserInteraction.CONTENT_TYPES]
            
            if interaction_type not in valid_interactions:
                return Response({
                    'error': f'Invalid interaction_type. Must be one of: {valid_interactions}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if content_type not in valid_content_types:
                return Response({
                    'error': f'Invalid content_type. Must be one of: {valid_content_types}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create the interaction
            interaction = UserInteraction.objects.create(
                user=request.user,
                interaction_type=interaction_type,
                content_type=content_type,
                content_id=int(content_id),
                duration_seconds=duration_seconds,
                search_query=search_query,
                referrer_type=referrer_type
            )
            
            # Update view count for the content if it's a view interaction
            if interaction_type == 'view':
                self._update_view_count(content_type, content_id)
            
            # Invalidate recommendation cache for this user
            self._invalidate_user_cache(request.user.id)
            
            return Response({
                'message': 'Interaction tracked successfully',
                'interaction_id': interaction.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error tracking interaction for user {request.user.id}: {e}")
            return Response({
                'error': 'Failed to track interaction'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _update_view_count(self, content_type: str, content_id: int):
        """Update the view count for the specified content"""
        try:
            if content_type == 'asset':
                Asset.objects.filter(id=content_id).update(
                    view_count=F('view_count') + 1
                )
            elif content_type == 'game':
                Game.objects.filter(id=content_id).update( 
                    view_count=F('view_count') + 1
                )
            elif content_type == 'job':
                Job.objects.filter(id=content_id).update(
                    view_count=F('view_count') + 1
                )
        except Exception as e:
            logger.warning(f"Failed to update view count for {content_type}:{content_id}: {e}")
    
    def _invalidate_user_cache(self, user_id: int):
        """Invalidate cached recommendations for a user"""
        cache_keys = [
            f"recommendations_{user_id}_asset_10",
            f"recommendations_{user_id}_game_10", 
            f"recommendations_{user_id}_job_10",
        ]
        cache.delete_many(cache_keys)


class SimilarContentAPIView(APIView):
    """Get similar content to a specific item"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, content_type, content_id):
        """Get similar content recommendations"""
        try:
            if content_type == 'asset':
                engine = MarketplaceRecommendations(request.user)
                similar_assets = engine.get_similar_assets(content_id, limit=5)
                
                return Response({
                    'similar_items': [{
                        'id': asset.id,
                        'title': asset.title,
                        'price': str(asset.price),
                        'rating': asset.rating,
                        'preview_image': asset.preview_image,
                        'seller': asset.seller.username,
                    } for asset in similar_assets]
                })
            
            # Add similar logic for games and jobs
            else:
                return Response({
                    'error': 'Similar content not yet implemented for this type'
                }, status=status.HTTP_501_NOT_IMPLEMENTED)
                
        except Exception as e:
            logger.error(f"Error getting similar content: {e}")
            return Response({
                'error': 'Failed to get similar content'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserPreferencesAPIView(APIView):
    """Manage user recommendation preferences"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get current user preferences"""
        try:
            prefs, created = UserPreference.objects.get_or_create(
                user=request.user
            )
            
            return Response({
                'preferences': {
                    'enable_recommendations': prefs.enable_recommendations,
                    'include_social_signals': prefs.include_social_signals,
                    'include_trending': prefs.include_trending,
                    'preferred_asset_types': prefs.preferred_asset_types,
                    'preferred_game_genres': prefs.preferred_game_genres,
                    'preferred_job_types': prefs.preferred_job_types,
                    'preferred_software': prefs.preferred_software,
                    'max_price_preference': str(prefs.max_price_preference) if prefs.max_price_preference else None,
                    'share_activity_for_recommendations': prefs.share_activity_for_recommendations,
                }
            })
            
        except Exception as e:
            logger.error(f"Error getting user preferences: {e}")
            return Response({
                'error': 'Failed to get preferences'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Update user preferences"""
        try:
            prefs, created = UserPreference.objects.get_or_create(
                user=request.user
            )
            
            # Update preference fields that are provided
            updateable_fields = [
                'enable_recommendations', 'include_social_signals', 'include_trending',
                'preferred_asset_types', 'preferred_game_genres', 'preferred_job_types',
                'preferred_software', 'max_price_preference', 'share_activity_for_recommendations'
            ]
            
            updated_fields = []
            for field in updateable_fields:
                if field in request.data:
                    setattr(prefs, field, request.data[field])
                    updated_fields.append(field)
            
            prefs.save()
            
            # Invalidate cache since preferences changed
            self._invalidate_user_cache(request.user.id)
            
            return Response({
                'message': 'Preferences updated successfully',
                'updated_fields': updated_fields
            })
            
        except Exception as e:
            logger.error(f"Error updating user preferences: {e}")
            return Response({
                'error': 'Failed to update preferences'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _invalidate_user_cache(self, user_id: int):
        """Invalidate cached recommendations for a user"""
        cache_keys = [
            f"recommendations_{user_id}_asset_10",
            f"recommendations_{user_id}_game_10", 
            f"recommendations_{user_id}_job_10",
        ]
        cache.delete_many(cache_keys)