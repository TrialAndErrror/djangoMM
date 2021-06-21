from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

#
# class User(models.Model):
#     name = models.CharField(max_length=150)
#     password = models.CharField(max_length=100)
#     email = models.EmailField(max_length=250)
#     date_created = models.DateTimeField(auto_now_add=True)
#
#     def __str__(self):
#         return f"{self.name} (User {self.id})"


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
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return f"{self.name} (Account {self.id})"


PERIOD_CHOICES = (
    ("day", "Daily"),
    ("week", "Weekly"),
    ("biweek", "Bi-Weekly"),
    ("month", "Monthly"),
    ("quarter", "Quarterly"),
    ("biyear", "Semi-Annual"),
    ("year", "Annual"),
)


class Bill(models.Model):
    name = models.CharField(max_length=150)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    variable = models.BooleanField(default=False)
    day = models.IntegerField(blank=True, null=True)
    period = models.CharField(
        max_length=20, choices=PERIOD_CHOICES, default="week", blank=True, null=True
    )
    last_paid = models.DateField(blank=True, null=True)
    next_due = models.DateField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return f"{self.name} (Bill {self.id})"

    def get_absolute_url(self):
        return reverse('frontend:bill_detail', kwargs={'pk': self.pk})




