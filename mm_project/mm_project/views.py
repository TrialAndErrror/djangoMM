from django.shortcuts import render, redirect, Http404
from api.models import User, Bill, Account
from api.forms import UserRegisterForm
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


def logout_view(request):
    logout(request)
    return render(request, "frontend/profile/loggedout.html", {})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('frontend:home')
    else:
        form = UserRegisterForm()
    return render(request, 'frontend/register.html', {'form': form})
