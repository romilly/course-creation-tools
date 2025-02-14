from django.urls import path
from . import views

urlpatterns = [
    path('', views.animate_brain, name='animate_brain'),
]
