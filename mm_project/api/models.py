from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

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
        return reverse('frontend:account_detail', kwargs={'pk': self.pk})


PERIOD_CHOICES = (
    ("Daily", "Daily"),
    ("Weekly", "Weekly"),
    ("Bi-Weekly", "Bi-Weekly"),
    ("Monthly", "Monthly"),
    ("Quarterly", "Quarterly"),
    ("Semi-Annual", "Semi-Annual"),
    ("Annual", "Annual"),
)


class Bill(models.Model):
    name = models.CharField(max_length=150)
    amount = models.FloatField()
    variable = models.BooleanField(default=False)
    day = models.IntegerField(blank=True, null=True)
    period = models.CharField(
        max_length=20, choices=PERIOD_CHOICES, default="Monthly", blank=True, null=True
    )
    last_paid = models.DateField(blank=True, null=True)
    next_due = models.DateField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    account = models.ForeignKey(Account, null=True, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return f"{self.name} ({self.period} Bill)"

    def get_absolute_url(self):
        return reverse('frontend:bill_detail', kwargs={'pk': self.pk})


EXPENSE_CHOICES = (
    ('Groceries', 'Groceries'),
    ('Pets', 'Pets'),
    ('Home', 'Home'),
    ('Transportation', 'Transportation'),
    ('Eating out', 'Eating out'),
    ('Entertainment', 'Entertainment'),
    ('Shopping', 'Shopping'),
    ('Skills', 'Skills'),
    ('Medical', 'Medical'),
    ('Other', 'Other'),
    ('Personal', 'Personal'),
    ('Donation', 'Donation'),
    ('Other', 'Other')
)


class Expense(models.Model):
    name = models.CharField(max_length=150)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    date = models.DateField()
    category = models.CharField(max_length=20, choices=EXPENSE_CHOICES, default='Groceries')
    other_category = models.CharField(max_length=150, null=True, blank=True, verbose_name='If Other, please specify:')
    notes = models.CharField(max_length=150, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return f"{self.name} ({self.category} Expense on {self.date})"

    def get_absolute_url(self):
        return reverse('frontend:expense_detail', kwargs={'pk': self.pk})
