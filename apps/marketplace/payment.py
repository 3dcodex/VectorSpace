"""
Payment Integration Module
Supports Stripe payment processing for marketplace and mentorship
"""

from django.conf import settings
from decimal import Decimal
import os

# Stripe configuration (add to settings.py or .env)
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET', '')

class PaymentProcessor:
    """
    Payment processor for handling transactions
    To integrate Stripe, install: pip install stripe
    """
    
    def __init__(self):
        self.stripe_enabled = bool(STRIPE_SECRET_KEY)
        if self.stripe_enabled:
            try:
                import stripe
                stripe.api_key = STRIPE_SECRET_KEY
                self.stripe = stripe
            except ImportError:
                self.stripe_enabled = False
    
    def create_payment_intent(self, amount, currency='usd', metadata=None):
        """
        Create a Stripe payment intent
        
        Args:
            amount: Amount in cents (e.g., 1000 for $10.00)
            currency: Currency code (default: 'usd')
            metadata: Additional data to attach to payment
        
        Returns:
            Payment intent object or None
        """
        if not self.stripe_enabled:
            return None
        
        try:
            intent = self.stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency,
                metadata=metadata or {},
            )
            return intent
        except Exception as e:
            print(f"Payment intent creation failed: {e}")
            return None
    
    def create_checkout_session(self, line_items, success_url, cancel_url, metadata=None):
        """
        Create a Stripe checkout session
        
        Args:
            line_items: List of items to purchase
            success_url: URL to redirect on success
            cancel_url: URL to redirect on cancel
            metadata: Additional data
        
        Returns:
            Checkout session object or None
        """
        if not self.stripe_enabled:
            return None
        
        try:
            session = self.stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=line_items,
                mode='payment',
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata or {},
            )
            return session
        except Exception as e:
            print(f"Checkout session creation failed: {e}")
            return None
    
    def verify_webhook_signature(self, payload, sig_header):
        """
        Verify Stripe webhook signature
        
        Args:
            payload: Request body
            sig_header: Stripe signature header
        
        Returns:
            Event object or None
        """
        if not self.stripe_enabled:
            return None
        
        try:
            event = self.stripe.Webhook.construct_event(
                payload, sig_header, STRIPE_WEBHOOK_SECRET
            )
            return event
        except Exception as e:
            print(f"Webhook verification failed: {e}")
            return None
    
    def process_asset_purchase(self, user, asset):
        """
        Process asset purchase
        
        Args:
            user: Buyer user object
            asset: Asset object to purchase
        
        Returns:
            Payment intent or checkout session
        """
        from .models import Transaction
        
        # Create transaction record
        transaction = Transaction.objects.create(
            user=user,
            transaction_type='asset_purchase',
            amount=asset.price,
            asset=asset,
            status='pending'
        )
        
        # Create payment intent
        metadata = {
            'transaction_id': transaction.id,
            'user_id': user.id,
            'asset_id': asset.id,
        }
        
        if self.stripe_enabled:
            intent = self.create_payment_intent(
                amount=float(asset.price),
                metadata=metadata
            )
            
            if intent:
                transaction.stripe_payment_id = intent.id
                transaction.save()
                return intent
        
        return None
    
    def complete_purchase(self, transaction_id):
        """
        Complete a purchase transaction
        
        Args:
            transaction_id: Transaction ID
        
        Returns:
            Boolean indicating success
        """
        from .models import Transaction, Purchase
        from django.utils import timezone
        
        try:
            transaction = Transaction.objects.get(id=transaction_id)
            
            if transaction.status == 'completed':
                return True
            
            # Create purchase record
            Purchase.objects.create(
                buyer=transaction.user,
                asset=transaction.asset,
                price_paid=transaction.amount
            )
            
            # Update transaction
            transaction.status = 'completed'
            transaction.completed_at = timezone.now()
            transaction.save()
            
            # Update asset downloads
            transaction.asset.downloads += 1
            transaction.asset.save()
            
            # Update seller wallet
            from .models import Wallet
            wallet, created = Wallet.objects.get_or_create(user=transaction.asset.seller)
            wallet.balance += transaction.amount
            wallet.total_earned += transaction.amount
            wallet.save()
            
            return True
        except Exception as e:
            print(f"Purchase completion failed: {e}")
            return False


# Singleton instance
payment_processor = PaymentProcessor()
