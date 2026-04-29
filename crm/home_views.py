from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

def home(request):
    """Home page - main dashboard"""
    if not request.user.is_authenticated:
        return redirect('/login')
    return render(request, 'index.html', {})

@csrf_exempt
def user_login(request):
    """User login page"""
    if request.user.is_authenticated:
        return redirect('/')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            error = 'Usuario o contraseña incorrectos'
            return render(request, 'login.html', {'error': error})
    
    return render(request, 'login.html', {})

def user_logout(request):
    """User logout"""
    logout(request)
    return redirect('/login')
