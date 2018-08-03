from django.urls import path, register_converter
from django.shortcuts import redirect, reverse
from . import views

app_name = 'explorer'


def redirect_home(request):
  return redirect('/summary/')

urlpatterns = [
  path('', redirect_home),
  path('summary/', views.summary, name = 'summary'),
  path('api/coords', views.get_coords, name = 'coords'),
  path('api/cloverleaf/<str:clade_txid>/<str:isotype>/', views.cloverleaf, name = 'cloverleaf'),
  path('api/tilemap/<str:clade_txid>/', views.tilemap, name = 'tilemap'),

  path('variation/', views.variation, name = 'variation'),
  path('api/distribution/<str:clades>/<str:isotypes>/<str:positions>/', views.distribution, name = 'distribution'),
  path('api/position/<str:clades>/<str:isotypes>/<str:positions>/', views.position_distribution, name = 'position'),

  path('compare/', views.compare, name = 'compare'),
  path('compare/render', views.render_bitchart, name = 'render'),
]
