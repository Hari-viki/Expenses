from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings

class CustomUser(AbstractUser):
    # You can add extra fields here if needed
    pass

class Bank(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ExpensesList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bank = models.CharField(max_length=100)
    date = models.DateField(default=timezone.now)
    total_amount = models.BigIntegerField(default=0)
    amount = models.BigIntegerField()
    balance_amount = models.BigIntegerField()
    description = models.CharField(max_length=1000)

    def __str__(self):
        return f"{self.user} - ₹{self.balance_amount} - {self.date}"

class BikeExpensesList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bike_model_name = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)
    petrol_amount = models.IntegerField(default=0)
    start_trip = models.IntegerField(default=0)
    end_trip = models.IntegerField(default=0)
    mileage = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user} - ₹{self.bike_model_name} - {self.mileage}"


