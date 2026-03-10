"""
Celery tasks for Vector Space background jobs and scheduled operations.
Includes reputation calculation with monitoring and alerting.
"""

import logging
import time
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from apps.core.reputation import ReputationManager

logger = logging.getLogger('reputation')


@shared_task(bind=True, max_retries=3)
def update_reputation_scores(self, verbose=False):
    """
    Daily task to recalculate all user reputation scores.
    
    Schedule (in settings.py):
        from celery.schedules import crontab
        
        CELERY_BEAT_SCHEDULE = {
            'update-reputation-scores': {
                'task': 'apps.core.tasks.update_reputation_scores',
                'schedule': crontab(hour=2, minute=0),  # 2 AM daily
            },
        }
    
    Monitoring:
    - Logs timing information
    - Alerts if execution > 5 minutes
    - Tracks failures and retries
    - Sends admin notifications on critical errors
    """
    start_time = time.time()
    task_id = self.request.id
    
    try:
        logger.info(f"[{task_id}] Starting reputation score update...")
        
        # Update scores
        result = ReputationManager.update_all_scores()
        
        elapsed_time = time.time() - start_time
        
        # Log success
        logger.info(
            f"[{task_id}] SUCCESS: {result} in {elapsed_time:.2f} seconds"
        )
        
        # Alert if slow (> 5 minutes)
        if elapsed_time > 300:
            logger.warning(
                f"[{task_id}] SLOW: Reputation update took {elapsed_time:.2f}s (threshold: 300s)"
            )
            send_alert_email(
                subject="⚠️  Slow reputation update",
                message=f"Reputation update took {elapsed_time:.2f}s (threshold: 5 min)\n\nCheck database queries.",
                alert_level="warning"
            )
        
        if verbose:
            logger.debug(f"[{task_id}] Reputation cache invalidated")
        
        return {
            'status': 'success',
            'task_id': task_id,
            'result': result,
            'duration_seconds': elapsed_time,
        }
    
    except Exception as exc:
        elapsed_time = time.time() - start_time
        
        logger.error(
            f"[{task_id}] FAILED: {str(exc)} after {elapsed_time:.2f}s",
            exc_info=True
        )
        
        # Send critical alert on failure
        send_alert_email(
            subject="🚨 Critical: Reputation update failed",
            message=f"Error: {str(exc)}\n\nCheck logs for details.",
            alert_level="critical"
        )
        
        # Retry with exponential backoff
        retry_delay = 60 * (2 ** self.request.retries)
        logger.info(f"[{task_id}] Retrying in {retry_delay}s (attempt {self.request.retries + 1}/3)")
        
        raise self.retry(exc=exc, countdown=retry_delay)


@shared_task(bind=True)
def update_single_user_score(self, user_id):
    """
    Update reputation score for a single user.
    Called when user's activity changes (new sale, game published, etc).
    
    Usage:
        from apps.core.tasks import update_single_user_score
        update_single_user_score.delay(user_id)
    """
    from apps.users.models import User
    from apps.core.models import RoleProgression
    
    try:
        user = User.objects.get(id=user_id)
        profile = user.profile
        
        logger.info(f"Updating score for user: {user.username}")
        
        # Update all applicable roles
        if profile.is_creator():
            profile.creator_score = ReputationManager.get_creator_score(user)
        
        if profile.is_developer():
            profile.developer_score = ReputationManager.get_developer_score(user)
        
        if profile.is_recruiter():
            profile.recruiter_score = ReputationManager.get_recruiter_score(user)
        
        if profile.is_mentor():
            profile.mentor_score = ReputationManager.get_mentor_score(user)
        
        profile.save()
        
        # Update progression
        for role_key in ['creator', 'developer', 'recruiter', 'mentor']:
            if getattr(profile, f'is_{role_key}')():
                score = getattr(profile, f'{role_key}_score')
                progression, _ = RoleProgression.objects.get_or_create(
                    user=user,
                    role=role_key
                )
                progression.update_progress(score)
        
        logger.info(f"Score updated for {user.username}")
        return {'status': 'success', 'user_id': user_id}
    
    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
        return {'status': 'error', 'user_id': user_id, 'error': 'User not found'}
    
    except Exception as exc:
        logger.error(f"Error updating score for user {user_id}: {str(exc)}", exc_info=True)
        return {'status': 'error', 'user_id': user_id, 'error': str(exc)}


@shared_task(bind=True)
def process_review_disputes(self):
    """
    Process pending review disputes.
    Moderators review disputes, this task handles auto-accept/reject logic.
    Run: Daily at 3 AM
    """
    from apps.core.models import ReviewDispute
    
    try:
        pending = ReviewDispute.objects.filter(status='pending')
        processed = 0
        
        for dispute in pending:
            # Auto-dismiss if no evidence after 14 days
            if (timezone.now() - dispute.created_at).days > 14 and not dispute.evidence_url:
                dispute.status = 'dismissed'
                dispute.moderator_decision = 'Auto-dismissed: No evidence provided'
                dispute.resolved_at = timezone.now()
                dispute.save()
                processed += 1
        
        logger.info(f"Processed {processed} review disputes")
        return {'status': 'success', 'processed': processed}
    
    except Exception as exc:
        logger.error(f"Error processing disputes: {str(exc)}", exc_info=True)
        return {'status': 'error', 'error': str(exc)}


@shared_task(bind=True)
def cleanup_expired_verifications(self):
    """
    Clean up expired role verifications.
    Run: Daily at 4 AM
    """
    from apps.core.models import RoleVerification
    
    try:
        expired = RoleVerification.objects.filter(
            status='approved',
            expires_at__lt=timezone.now()
        ).update(status='expired')
        
        logger.info(f"Expired {expired} role verifications")
        return {'status': 'success', 'expired': expired}
    
    except Exception as exc:
        logger.error(f"Error cleaning up verifications: {str(exc)}", exc_info=True)
        return {'status': 'error', 'error': str(exc)}


def send_alert_email(subject, message, alert_level='info'):
    """
    Send alert email to admins.
    
    Args:
        subject: Email subject
        message: Email body
        alert_level: 'info', 'warning', or 'critical'
    """
    try:
        # Add emoji based on level
        icons = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'critical': '🚨',
        }
        
        full_subject = f"{icons.get(alert_level, 'ℹ️')} [Vector] {subject}"
        
        # Only send for warning/critical
        if alert_level in ['warning', 'critical']:
            admin_emails = [admin[1] for admin in settings.ADMINS]
            
            if admin_emails:
                send_mail(
                    full_subject,
                    f"{message}\n\nTimestamp: {timezone.now().isoformat()}",
                    settings.DEFAULT_FROM_EMAIL,
                    admin_emails,
                    fail_silently=True,
                )
        
        logger.log(
            level=logging.WARNING if alert_level == 'warning' else logging.CRITICAL,
            msg=f"[{alert_level.upper()}] {subject}: {message}"
        )
    
    except Exception as e:
        logger.error(f"Failed to send alert email: {str(e)}")


# For development/testing with Django shell
def run_score_update_sync():
    """
    Run reputation update synchronously (for testing without Celery).
    Usage: python manage.py shell
        >>> from apps.core.tasks import run_score_update_sync
        >>> run_score_update_sync()
    """
    logger.info("Running reputation update (synchronous)")
    start = time.time()
    result = ReputationManager.update_all_scores()
    elapsed = time.time() - start
    logger.info(f"Completed: {result} in {elapsed:.2f}s")
    return result
