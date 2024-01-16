"""
Database models.
"""
import os
from dotenv import load_dotenv
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
import stripe

from app import settings

# Create your models here.

load_dotenv()


stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

class MemberManager(BaseUserManager):
    """Custom user manager for the Member model."""
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        # Setting up Stripe customer and associating the ID with the user
        stripe_customer = stripe.Customer.create(email=email, api_key=os.getenv("STRIPE_SECRET_KEY"))
        user.stripe_customer_id = stripe_customer.id
        user.save()

        return user
    
    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user

class Member(AbstractBaseUser, PermissionsMixin):
    """User model with the name 'Member'."""
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_premium = models.BooleanField(default=False)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    subscription_status = models.BooleanField(default=False)
    subscription_id = models.CharField(max_length=50, blank=True, null=True)

    objects = MemberManager()

    USERNAME_FIELD = 'email'
