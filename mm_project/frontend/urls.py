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
from .views import *


app_name = "frontend"

urlpatterns = [
    path("", frontend_home, name="home"),
    path("profile/", view_profile, name="profile"),
    path("summary/", view_summary, name="summary"),
    path("bills/", view_all_bills, name="all_bills"),
    path("bills/add", BillCreateView.as_view(), name="add_bill"),
    path('bills/<int:pk>/', BillDetailView.as_view(), name='bill_detail'),
    path("bills/<int:pk>/update/", BillUpdateView.as_view(), name="bill_update"),
    path("bills/<int:pk>/delete/", BillDeleteView.as_view(), name="bill_delete"),
    path("accounts/", view_all_accounts, name="all_accounts"),
    path("accounts/add", AccountCreateView.as_view(), name="add_account"),
    path("accounts/<int:pk>", AccountDetailView.as_view(), name="account_detail"),
    path("accounts/<int:pk>/update/", AccountUpdateView.as_view(), name="account_update"),
    path("accounts/<int:pk>/delete/", AccountDeleteView.as_view(), name="account_delete"),
]
