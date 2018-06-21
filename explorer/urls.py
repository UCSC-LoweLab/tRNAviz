from django.urls import path, register_converter
from django.shortcuts import redirect, reverse
from . import views

app_name = 'explorer'


def redirect_home(request):
  return redirect('/summary/')

urlpatterns = [
  path('', redirect_home),
  path('summary/', views.summary, name = 'summary'),
  path('api/cloverleaf', views.cloverleaf, name = 'cloverleaf')
]
