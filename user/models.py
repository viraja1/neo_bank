from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    phone_no = models.CharField(max_length=100)
    wallet_id = models.CharField(max_length=100)
    contact_id = models.CharField(max_length=100)
    card_id = models.CharField(max_length=100)
