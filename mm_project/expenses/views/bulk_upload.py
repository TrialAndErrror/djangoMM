import csv

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from accounts.models import Account
from expenses.forms import CSVUploadForm
from expenses.models import Expense


@login_required
def upload_csv(request):
    duplicate_entries = []
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            decoded_file = file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)

            for row in reader:
                if "-" in row['Amount']:
                    row_amount = row['Amount'].replace('-', '')
                else:
                    row_amount = f"-{row['Amount']}"


                try:
                    Expense.objects.update_or_create(
                        name=row['Description'],
                        amount=row_amount,
                        date=row['Date'],
                        owner=request.user,
                        account_id=request.POST['account'],
                        defaults={
                            "notes": row['Original Description'],
                            "category": row['Category'],
                        }
                    )
                except Expense.MultipleObjectsReturned:
                    duplicate_entries.append(
                        {"date": row['Date'], "description": row['Description'], "amount": row['Amount']})
                    continue

            messages.success(request, "CSV file successfully uploaded and processed.")


    else:
        form = CSVUploadForm()
        form.fields['account'].queryset = Account.objects.filter(owner=request.user)
    return render(request, 'upload_csv.html', {'form': form, "duplicates": duplicate_entries})
