from django.urls import path
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from . import views

urlpatterns=[
    path('', views.index,name="preferences")
]