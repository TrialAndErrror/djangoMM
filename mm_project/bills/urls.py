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

from bills.views import view_all_bills, pay_bill, BillDetailView, BillUpdateView, BillDeleteView


app_name = "bills"

urlpatterns = [
    path("", view_all_bills, name="all_bills"),
    path("add", BillCreateView.as_view(), name="add_bill"),
    path('<int:pk>/', BillDetailView.as_view(), name='bill_detail'),
    path("<int:pk>/update/", BillUpdateView.as_view(), name="bill_update"),
    path("<int:pk>/delete/", BillDeleteView.as_view(), name="bill_delete"),
    path("<int:pk>/pay/", pay_bill, name="pay_bill"),
]
