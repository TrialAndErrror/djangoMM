from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

# Create your models here.
ACCOUNT_CHOICES = (
    ("Checking", "Checking"),
    ("Savings", "Savings"),
    ("Credit", "Credit"),
    ("Money Market", "Money Market"),
    ("CD", "Certificate of Deposit"),
    ("IRA", "IRA"),
    ("Brokerage", "Brokerage"),
    ("Other", "Other"),
)


class Account(models.Model):
    name = models.CharField(max_length=150)
    balance = models.DecimalField(decimal_places=2, max_digits=10)
    type = models.CharField(max_length=20, choices=ACCOUNT_CHOICES, default="checking")
    last_update = models.DateField('Last Updated', auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return f"{self.name} ({self.type} Account)"

    def get_absolute_url(self):
        return reverse('accounts:account_detail', kwargs={'pk': self.pk})
