from django.contrib import admin
from .models import Offer, OfferDetail


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """Admin configuration for Offer."""
    list_display = ('id', 'title', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('title', 'description')


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """Admin configuration for OfferDetail."""
    list_display = ('id', 'offer', 'offer_type', 'price', 'delivery_time_in_days')
    list_filter = ('offer_type',)