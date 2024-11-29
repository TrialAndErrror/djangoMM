import csv

from expenses.models import Expense


class User:
    pass


class USAACsvIngest:
    expected_headers = [
        'Date',
        'Description',
        'Original Description',
        'Category',
        'Amount',
        'Status'
    ]
    reader: csv.DictReader
    duplicate_entries: list

    @classmethod
    def is_valid(cls, headers):
        return sorted(headers) == sorted(cls.expected_headers)

    def __init__(self, reader: csv.DictReader, user: User, account_id: str):

        self.reader = reader
        self.user = user
        self.account_id = account_id

        self.duplicate_entries = []

    def process(self):
        for row in self.reader:
            
            # Skip deposits, just use expenses
            if "-" not in row['Amount']:
                continue
                
            row_amount = row['Amount'].replace('-', '')

            try:
                Expense.objects.update_or_create(
                    name=row['Description'],
                    amount=row_amount,
                    date=row['Date'],
                    owner=self.user,
                    account_id=self.account_id,
                    defaults={
                        "notes": row['Original Description'],
                        "category": row['Category'],
                    }
                )
            except Expense.MultipleObjectsReturned:
                self.duplicate_entries.append(
                    {"date": row['Date'], "description": row['Description'], "amount": row['Amount']})
