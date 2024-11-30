from django.core.management.base import BaseCommand

from expenses.models import ExpenseCategory


class Command(BaseCommand):
    help = "Create default ExpenseCategory objects"

    def handle(self, *args, **kwargs):
        default_categories = [
            {"name": "Groceries", "description": "Expenses for food and household supplies."},
            {"name": "Pets", "description": "Expenses related to pet care, food, and accessories."},
            {"name": "Home", "description": "Expenses for home maintenance, rent, or mortgage."},
            {"name": "Transportation", "description": "Expenses for commuting, fuel, or public transport."},
            {"name": "Eating Out", "description": "Expenses for dining at restaurants or takeout."},
            {"name": "Entertainment", "description": "Expenses for movies, games, or outings."},
            {"name": "Shopping", "description": "Expenses for clothing, gadgets, or other items."},
            {"name": "Skills", "description": "Expenses for learning new skills or education."},
            {"name": "Medical", "description": "Expenses for healthcare, prescriptions, or medical bills."},
            {"name": "Other", "description": "Miscellaneous expenses that don't fit other categories."},
            {"name": "Personal", "description": "Expenses for personal care and grooming."},
            {"name": "Donation", "description": "Expenses for charity or contributions to causes."},
        ]
        
        created_count = 0
        for category in default_categories:
            obj, created = ExpenseCategory.objects.get_or_create(
                name=category["name"],
                defaults={"description": category["description"]},
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully added {created_count} ExpenseCategory objects."
            )
        )
