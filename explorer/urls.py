from django.urls import path, register_converter
from . import views

app_name = 'explorer'

urlpatterns = [
  path('', views.summary, name = 'summary'),
]
