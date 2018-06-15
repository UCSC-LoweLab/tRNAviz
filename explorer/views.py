from django.shortcuts import render
from django.shortcuts import redirect
from . import models
from . import filters
import pdb

def summary(request):
  trna_list = models.tRNA.objects.filter(genus = 'Saccharomyces')
  plot_data = generate_plot_data(trna_list)
  return render(request, 'explorer/summary.html', {
    'plot_data': plot_data,
  })


def generate_plot_data(queryset):
  # df = read_frame(queryset)
  # consensus = build_consensus(df)
  return queryset
  # for isotype in isotypes:
  #   consbuild_consensus()

  # {'position', 'isotype', 'consensus_feature', 'freqs': {'A', 'G', 'C', 'U', '-'}}


def build_consensus():
  pass