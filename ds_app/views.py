from django.shortcuts import render

def home(request):
    return render(request, 'ds_app/home.html')
