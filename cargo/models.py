from django.db import models
from django.utils import timezone

from users.models import User

class Cargo(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET, related_name='cargo_owner')
    pickup_location = models.CharField(max_length=255)
    delivery_location = models.CharField(max_length=255)
    cargo_details = models.TextField()
    status = models.CharField(max_length=20, default='pending')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cargo_assignee')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

