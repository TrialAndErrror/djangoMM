from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from accounts.models import Account

# Create your models here.
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
        return reverse('expenses:expense_detail', kwargs={'pk': self.pk})
