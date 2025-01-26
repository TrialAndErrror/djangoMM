from django.urls import path

from expenses.views.budgets import BudgetUpdateView, BudgetCreateView, BudgetDetailView, \
    BudgetListView
from expenses.views.bulk_upload import upload_csv
from expenses.views.entries import ExpenseCreateView, ExpenseDetailView, ExpenseUpdateView, \
    ExpenseDeleteView, ViewExpensesList, edit_field_inline
from expenses.views.reports import MonthlyExpenseReportView

app_name = "expenses"

urlpatterns = [
    path("", ViewExpensesList.as_view(), name="all_expenses"),
    path("add", ExpenseCreateView.as_view(), name="add_expense"),
    path("<int:pk>", ExpenseDetailView.as_view(), name="expense_detail"),
    path("<int:pk>/update/", ExpenseUpdateView.as_view(), name="expense_update"),
    path("<int:pk>/delete/", ExpenseDeleteView.as_view(), name="expense_delete"),
    path('upload-csv/', upload_csv, name='upload_csv'),
    path('edit-inline/<int:expense_id>/<field>', edit_field_inline, name='expense_field_edit'),

    path('budget/', BudgetListView.as_view(), name='budget_list'),
    path('budget/create/', BudgetCreateView.as_view(), name='budget_create'),
    path('budget/edit/<int:pk>/', BudgetUpdateView.as_view(), name='budget_edit'),
    path('budget/view/<int:pk>/', BudgetDetailView.as_view(), name='budget_view'),

    path('reports/monthly/', MonthlyExpenseReportView.as_view(), name='reports_monthly'),

]
