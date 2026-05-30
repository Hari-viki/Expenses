from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings

class CustomUser(AbstractUser):
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True
    )

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
    extra_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.CharField(max_length=1000)

    def __str__(self):
        return f"{self.user} - ₹{self.balance_amount} - {self.date}"

class BikeExpensesList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bike_image = models.ImageField(
        upload_to='bike_image/',
        null=True,
        blank=True
    )
    date = models.DateField(default=timezone.now)
    petrol_amount = models.IntegerField(default=0)
    start_trip = models.IntegerField(default=0)
    end_trip = models.IntegerField(default=0)
    mileage = models.IntegerField(default=0)
    licence_image = models.ImageField(
        upload_to='lice_img/',
        null=True,
        blank=True
    )
    rc_image =  models.ImageField(
        upload_to='rc_img/',
        null=True,
        blank=True
    )
    insurance_image =  models.ImageField(
        upload_to='ins_img/',
        null=True,
        blank=True
    )

    
    def __str__(self):
        return f"{self.user} - ₹{self.date} - {self.mileage}"


class BikeTrip(models.Model):
    user          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date          = models.DateField(default=timezone.now)
    petrol_amount = models.IntegerField(default=0)
    start_trip    = models.IntegerField(default=0)
    end_trip      = models.IntegerField(default=0)
    mileage       = models.IntegerField(default=0)
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.user} - {self.date} - ₹{self.petrol_amount}"

    @property
    def km_travelled(self):
        return max(0, self.end_trip - self.start_trip)