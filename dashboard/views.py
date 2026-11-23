
from django.shortcuts import render, redirect


def dashboard_view(request):
    if not request.session.get('demo_logged_in'):
        return redirect('login')
    return render(request, 'dashboard/home.html')
