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
from accounts.views import view_all_accounts, AccountDetailView, AccountCreateView, AccountUpdateView, \
    AccountDeleteView, htmx_get_balance

app_name = "accounts"

urlpatterns = [

    path("", view_all_accounts, name="all_accounts"),
    path("add", AccountCreateView.as_view(), name="add_account"),
    path("<int:pk>", AccountDetailView.as_view(), name="account_detail"),
    path("<int:pk>/update/", AccountUpdateView.as_view(), name="account_update"),
    path("<int:pk>/delete/", AccountDeleteView.as_view(), name="account_delete"),
    path("htmx/get-balance/", htmx_get_balance, name="get_balance"),

]
