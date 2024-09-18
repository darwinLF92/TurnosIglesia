# aplicacion/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required


@login_required(login_url='/login/')
def home_view(request):
    return render(request, 'aplicacion/home.html')

def login_view(request):
    error_message = None
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('aplicacion:home')
        else:
            error_message = 'Usuario o contraseña inválidos'
    return render(request, 'aplicacion/login.html', {'error_message': error_message})


def logout_view(request):
    logout(request)
    return redirect('aplicacion:login')  # Redirige al usuario a la página de inicio de sesión después de cerrar sesión