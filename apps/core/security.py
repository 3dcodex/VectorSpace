"""
Security and utility functions
"""
from django.utils.html import escape
from functools import wraps
from django.core.exceptions import PermissionDenied
import logging

logger = logging.getLogger(__name__)

def sanitize_search_input(query: str, max_length: int = 100) -> str:
    """Sanitize user search input"""
    if not query:
        return ''
    query = escape(query.strip())
    query = query[:max_length]
    return query

def creator_required(view_func):
    """Decorator to require creator role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied('Authentication required')
        if not request.user.profile.is_creator():
            logger.warning(f'User {request.user.id} attempted creator-only action without role')
            raise PermissionDenied('Creator role required')
        return view_func(request, *args, **kwargs)
    return wrapper

def developer_required(view_func):
    """Decorator to require developer role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied('Authentication required')
        if not request.user.profile.is_developer():
            logger.warning(f'User {request.user.id} attempted developer-only action without role')
            raise PermissionDenied('Developer role required')
        return view_func(request, *args, **kwargs)
    return wrapper

def recruiter_required(view_func):
    """Decorator to require recruiter role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied('Authentication required')
        if not request.user.profile.is_recruiter():
            logger.warning(f'User {request.user.id} attempted recruiter-only action without role')
            raise PermissionDenied('Recruiter role required')
        return view_func(request, *args, **kwargs)
    return wrapper

def mentor_required(view_func):
    """Decorator to require mentor role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied('Authentication required')
        if not request.user.profile.is_mentor():
            logger.warning(f'User {request.user.id} attempted mentor-only action without role')
            raise PermissionDenied('Mentor role required')
        return view_func(request, *args, **kwargs)
    return wrapper
