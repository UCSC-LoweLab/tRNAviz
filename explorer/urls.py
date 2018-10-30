from django.urls import path, re_path
from django.shortcuts import redirect, reverse
from django.conf import settings
from . import views
from . import services
from . import compare

app_name = 'explorer'


def redirect_home(request):
  return redirect('/summary/')

urlpatterns = [
  path('', redirect_home),
  path('summary/', views.summary, name = 'summary'),
  path('search/<str:search_type>', services.search, name = 'search'),
  path('api/coords', services.get_coords, name = 'coords'),
  path('summary/taxonomy/<str:clade_txid>/<str:isotype>', services.taxonomy_summary, name = 'taxonomy_summary'),
  path('summary/domain_features/<str:clade_txid>/<str:isotype>', services.domain_features, name = 'domain_features'),
  path('summary/anticodon_counts/<str:clade_txid>/<str:isotype>', services.anticodon_counts, name = 'anticodon_counts'),
  path('summary/isotype_discrepancies/<str:clade_txid>/<str:isotype>', services.isotype_discrepancies, name = 'isotype_discrepancies'),

  path('api/cloverleaf/<str:clade_txid>/<str:isotype>/', services.cloverleaf, name = 'cloverleaf'),
  path('api/tilemap/<str:clade_txid>/', services.tilemap, name = 'tilemap'),

  path('variation/distribution', views.variation_distribution, name = 'variation_distribution'),
  path('variation/species', views.variation_species, name = 'variation_species'),
  path('api/distribution/<str:clade_txids>/<str:isotypes>/<str:positions>/', services.distribution, name = 'distribution'),
  path('api/species/<str:clade_txids>/<str:foci>/', services.species_distribution, name = 'species_distribution'),

  path('compare/', views.compare, name = 'compare'),
  re_path('api/bitchart/(?P<formset_json>.+)', compare.bitchart, name = 'bitchart'),

  path('about/', views.about, name = 'about'),
  path('api/genome_summary/', services.genome_summary, name = 'genome_summary_dynamic'),
  path('api/genome_summary/<str:taxonomy_id>', services.genome_summary, name = 'genome_summary'),
  path('api/score_summary_taxonomy/', services.score_summary_taxonomy, name = 'score_summary_taxonomy_dynamic'),
  path('api/score_summary_taxonomy/<str:taxonomy_id>', services.score_summary_taxonomy, name = 'score_summary_taxonomy'),
  path('api/score_summary_isotype/', services.score_summary_isotype, name = 'score_summary_isotype_dynamic'),
  path('api/score_summary_isotype/<str:taxonomy_id>', services.score_summary_isotype, name = 'score_summary_isotype'),


  path('taxonomy/', views.taxonomy, name = 'taxonomy'),
  path('taxonomy/visualize_itol/<str:taxonomy_id>', views.visualize_itol, name = 'visualize_itol'),
  path('taxonomy/visualize_itol/', views.visualize_itol, name = 'visualize_itol_dynamic'),
  path('api/newick_tree/<str:taxonomy_id>', services.newick_tree, name = 'newick_tree'),
]
