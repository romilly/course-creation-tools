from django.shortcuts import render

# Create your views here.

def animate_brain(request):
    return render(request, 'animator/animate.html')
