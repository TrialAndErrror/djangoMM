from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

from accounts.models import Account


class ExpenseCategory(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class Expense(models.Model):
    name = models.CharField(max_length=150)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    date = models.DateField()
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, blank=True, null=True)
    notes = models.CharField(max_length=150, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return f"{self.name} ({self.category} Expense on {self.date})"

    def get_absolute_url(self):
        return reverse('expenses:expense_detail', kwargs={'pk': self.pk})

    def get_short_name(self):
        if len(self.name) > 13:
            return f'{self.name[:10]}...'
        return self.name


class CategoryBudget(models.Model):
    category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, blank=True, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
