from django.contrib import admin
from .models import Cargo


@admin.register(Cargo)
class CargoAdmin(admin.ModelAdmin):
    list_display = ('user_phone_number', 'pickup_location', 'delivery_location', 'cargo_details', 'status', 'assigned_to', 'created_at')

    def user_phone_number(self, obj):
        return obj.user.phone_number