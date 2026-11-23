
from django.shortcuts import render, redirect


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Dummy login credentials
        if username == 'admin' and password == 'admin123':
            request.session['demo_logged_in'] = True
            return redirect('dashboard')
        else:
            return render(request, 'accounts/login.html', {
                'error': 'Invalid username or password'
            })
    return render(request, 'accounts/login.html')


def logout_view(request):
    request.session.flush()
    return redirect('login')
