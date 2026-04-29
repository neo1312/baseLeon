from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def home(request):
    """Home page - main dashboard"""
    return render(request, 'index.html', {})
