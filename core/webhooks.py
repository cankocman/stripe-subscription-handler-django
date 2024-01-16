"""Description: Webhook handlers for Stripe events"""
import logging
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import stripe

from app import settings

Member = get_user_model()

stripe.api_key = settings.STRIPE_SECRET_KEY
endpoint_secret = settings.STRIPE_ENDPOINT_SECRET

logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
def stripe_webhook(request):
    """Constructs and handles Stripe events"""

    payload = request.body
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logger.error("Invalid payload: %s", e)
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error("Invalid signature: %s", e)
        return HttpResponse(status=400)

    if event['type'] == 'invoice.payment_succeeded':
        print("Payment succeeded")
        handle_payment_success(event)


    elif event['type'] == 'invoice.payment_succeeded':
        handle_payment_failed(event)

    elif event['type'] == 'checkout.session.completed':
        handle_checkout_session_completed(event)

    elif event['type'] == 'customer.subscription.updated':
        handle_subscription_updated(event)

    return HttpResponse(status=200)

def handle_payment_success(event):
    """Extracts necessary information from the event"""
    customer_id = event['data']['object']['customer']
    subscription_id = event['data']['object']['subscription']

    try:
        subscription = stripe.Subscription.retrieve(subscription_id)

        # Updating the Member model
        try:
            print("Updating Member model.")
            member = Member.objects.get(stripe_customer_id=customer_id)
            member.subscription_status = subscription['status'] == 'active'
            member.subscription_id = subscription_id
            member.save()
            logger.info("Subscription status updated for: %s", customer_id)
        except Member.DoesNotExist:
            logger.error("Member does not exist: %s", customer_id)

    except stripe.error.StripeError as e:
        logger.error("Stripe error during subscription verification: %s", str(e))

def handle_payment_failed(event):
    """Informs if the payment failed"""
    logger.warning("Payment failed for subscription: %s", event['data']['object']['subscription'])

def handle_checkout_session_completed(event):
    """Informs if the checkout session has been completed"""
    logger.info("Checkout completed for subscription: %s", event['data']['object']['subscription'])

def handle_subscription_updated(event):
    """Informs if the subscription has been updated"""
    logger.info("Subscription updated: %s", event['data']['object']['subscription'])
