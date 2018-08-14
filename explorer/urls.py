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

  path('variation/', views.variation_distribution, name = 'variation'),
  path('variation/distribution', views.variation_distribution, name = 'variation_distribution'),
  path('variation/species', views.variation_species, name = 'variation_species'),
  path('api/distribution/<str:clade_txids>/<str:isotypes>/<str:positions>/', views.distribution, name = 'distribution'),
  path('api/species/<str:clade_txids>/<str:foci>/', views.species_distribution, name = 'species_distribution'),

  path('compare/', views.compare, name = 'compare'),
  # path('compare/render', views.render_bitchart, name = 'render'),
]
