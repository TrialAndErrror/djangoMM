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
from .views import frontend_home, view_profile, view_all_bills, view_all_accounts, \
    BillCreateView, AccountCreateView, BillDetailView


app_name = "frontend"

urlpatterns = [
    path("", frontend_home, name="home"),
    path("profile/", view_profile, name="profile"),
    path("bills/", view_all_bills, name="all_bills"),
    path('bills/<int:pk>/', BillDetailView.as_view(), name='bill_detail'),
    path("bills/add", BillCreateView.as_view(), name="add_bill"),
    path("accounts/", view_all_accounts, name="all_accounts"),
    path("accounts/add", AccountCreateView.as_view(), name="add_account"),

]
