from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from accounts.models import Account

# Create your models here.
PERIOD_CHOICES = (
    (1, "Daily"),
    (7, "Weekly"),
    (14, "Bi-Weekly"),
    (30, "Monthly"),
    (365, "Annual"),
)


class Bill(models.Model):
    name = models.CharField(max_length=150)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    variable = models.BooleanField(default=False)
    day = models.IntegerField(blank=True, null=True)
    period = models.IntegerField(choices=PERIOD_CHOICES, default=30, blank=True, null=True)
    last_paid = models.DateField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, default=None)

    @property
    def next_due(self):
        return self.last_paid + timedelta(days=self.period)

    def __str__(self):
        return f"{self.name} ({self.period} Bill)"

    def get_absolute_url(self):
        return reverse('bills:bill_detail', kwargs={'pk': self.pk})
