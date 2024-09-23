"""mm_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path

from expenses.views import ExpenseDetailView, ExpenseCreateView, ExpenseUpdateView, ExpenseDeleteView, \
    view_all_expenses

app_name = "expenses"

urlpatterns = [
    path("", view_all_expenses, name="all_expenses"),
    path("add", ExpenseCreateView.as_view(), name="add_expense"),
    path("<int:pk>", ExpenseDetailView.as_view(), name="expense_detail"),
    path("<int:pk>/update/", ExpenseUpdateView.as_view(), name="expense_update"),
    path("<int:pk>/delete/", ExpenseDeleteView.as_view(), name="expense_delete"),
]
