# core/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Member

class MemberAdmin(UserAdmin):
    model = Member
    list_display = ('email', 'is_staff', 'is_active', 'is_premium', 'stripe_customer_id', 'subscription_status', 'subscription_id')
    list_filter = ('is_staff', 'is_active', 'is_premium', 'subscription_status')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_staff', 'is_active', 'is_premium')}),
        ('Stripe Information', {'fields': ('stripe_customer_id', 'subscription_status', 'subscription_id')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_staff', 'is_active', 'is_premium', 'stripe_customer_id', 'subscription_status', 'subscription_id'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(Member, MemberAdmin)
