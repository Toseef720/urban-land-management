from django.shortcuts import render, redirect
from .models import Property
from .forms import PropertyForm


def property_list(request):
    if not request.session.get('demo_logged_in'):
        return redirect('login')
    properties = Property.objects.all().order_by('-created_at')
    return render(request, 'properties/property_list.html', {
        'properties': properties
    })


def add_property(request):
    if not request.session.get('demo_logged_in'):
        return redirect('login')
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('property_list')
    else:
        form = PropertyForm()
    return render(request, 'properties/add_property.html', {
        'form': form
    })


def edit_property(request, property_id):
    if not request.session.get('demo_logged_in'):
        return redirect('login')
    property = Property.objects.get(id=property_id)
    if request.method == 'POST':
        form = PropertyForm(
            request.POST,
            request.FILES,
            instance=property
        )
        if form.is_valid():
            form.save()
            return redirect('property_list')
    else:
        form = PropertyForm(instance=property)
    return render(request, 'properties/edit_property.html', {
        'form': form,
        'property': property
    })


def delete_property(request, property_id):
    if not request.session.get('demo_logged_in'):
        return redirect('login')
    if request.method == 'POST':
        property = Property.objects.get(id=property_id)
        property.delete()
    return redirect('property_list')