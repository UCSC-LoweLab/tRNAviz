from django.shortcuts import render
from django.shortcuts import redirect
from django.db.models import Count, Max
from django.core import serializers
from rest_framework.renderers import JSONRenderer
from collections import defaultdict
from django.http import JsonResponse
import json

import pdb

from . import models
from . import filters
from . import serializers


def summary(request):
  filter_clade = 'Saccharomyces'
  filter_rank = 'genus'
  filter_isotype = 'All'

  clades_qs = models.Consensus.objects.values('clade', 'rank')
  clades = {pair['clade']: pair['rank'] for pair in clades_qs}

  if request.method == "POST":
    filter_clade = request.POST.get('clade')
    filter_rank = clades[filter_clade]
    filter_isotype = request.POST.get('isotype')

  return render(request, 'explorer/summary.html', {
    'clade': filter_clade,
    'rank': filter_rank,
    'isotype': filter_isotype,
    'clades': clades
  })


SINGLE_POSITIONS = [
  '8', '9',
  '14', '15', '16', '17', '17a', '18', '19', '20', '20a', '20b', '21',
  '26',
  '32', '33', '34', '35', '36', '37', '38', 
  '44', '45', '46', '47', '48', 
  'V1', 'V2', 'V3', 'V4', 'V5',
  '54', '55', '56', '57', '58', '59', '60', 
  '73'
]
PAIRED_POSITIONS = [
  '1:72', '2:71', '3:70', '4:69', '5:68', '6:67', '7:66',
  '10:25', '11:24', '12:23', '13:22', 
  '27:43', '28:42', '29:41', '30:40', '31:39', 
  'V11:V21', 'V12:V22', 'V13:V23', 'V14:V24', 'V15:V25', 'V16:V26', 'V17:V27', 
  '49:65', '50:64', '51:63', '52:62', '53:61', 
]

FEATURE_LABELS = {
  'A': 'A', 'G': 'G', 'C': 'C', 'U': 'U', 'Absent': '-', '': '',
  'Purine': 'Purine', 'Pyrimidine': 'Pyrimidine',
  'Amino': 'A / C', 'Keto': 'G / U', 'Weak': 'A / U', 'Strong': 'G / C', 
  'B': 'C / G / U', 'H': 'A / C / U', 'D': 'A / G / U', 'V': 'A / C / G', 'N': 'N', 
  'GC': ('G', 'C'), 'AU': ('A', 'U'), 'UA': ('U', 'A'), 'CG': ('C', 'G'), 'GU': ('G', 'U'), 'UG': ('U', 'G'),
  'PurinePyrimidine': ('Purine', 'Pyrimidine'), 'PyrimidinePurine': ('Pyrimidine', 'Purine'), 'WobblePair': ('G / U', 'G / U'),
  'StrongPair': ('G / C', 'G / C'), 'WeakPair': ('A / U', 'A / U'), 'AminoKeto': ('A / C', 'G / U'), 'KetoAmino': ('G / U', 'A / C'),
  'Paired': ('Paired', 'Paired'), 'Bulge': ('Bulge', 'Bulge'), 'Mismatched': ('Mismatched', 'Mismatched'), 'NN': ('N', 'N')
}

SINGLE_FEATURES = ['A', 'C', 'G', 'U', 'absent']
PAIRED_FEATURES = {
  'AU': 'A:U', 'UA': 'U:A', 'GC': 'G:C', 'CG': 'C:G', 'GU': 'G:U', 'UG': 'U:G', 
  'AA': 'A:A', 'AC': 'A:C', 'AG': 'A:G', 'CA': 'C:A', 'CC': 'C:C', 'CU': 'C:U', 'GA': 'G:A', 'GG': 'G:G', 'UC': 'U:C', 'UU': 'U:U',
  'AM': 'A:-', 'CM': 'C:-', 'GM': 'G:-', 'UM': 'U:-', 'MA': '-:A', 'MC': '-:C', 'MG': '-:G', 'MU': '-:U', 'MM': '-:-'
}

ISOTYPES = ['Ala', 'Arg', 'Asn', 'Asp', 'Cys', 'Gln', 'Glu', 'Gly', 'His', 'Ile', 'iMet', 'Leu', 'Lys', 'Met', 'Phe', 'Pro', 'Ser', 'Thr', 'Trp', 'Tyr', 'Val']


def process_freqs_to_json(clade = 'Saccharomyces'):
  queryset = models.Freq.objects.filter(clade = clade).values('position', 'isotype', 'A', 'G', 'C', 'U', 'absent')
  plot_data = defaultdict(dict)
  for row in queryset:
    plot_data[row['isotype']][row['position']] = {key:row[key] for key in row}
  return plot_data


def get_coords(request):
  data = models.Coord.objects.all()
  serializer = serializers.CoordSerializer(data, many = True)
  return JsonResponse(serializer.data, safe = False)

def cloverleaf(request, clade, isotype):
  consensus_qs = models.Consensus.objects.filter(clade = clade, isotype = isotype)
  freqs_qs = models.Freq.objects.filter(clade = clade, isotype = isotype)
  plot_data = {}

  # preprocess freqs so Django doesn't submit separate queries per filter
  freqs = {}
  for freq in freqs_qs.values():
    position = freq['position']
    if position in SINGLE_POSITIONS:
      freqs[position] = {base: freq[base] for base in SINGLE_FEATURES}
    elif position in PAIRED_POSITIONS:
      freqs[position] = {PAIRED_FEATURES[pair]: freq[pair] for pair in PAIRED_FEATURES}

  consensus = consensus_qs.values()[0]
  for colname in consensus:
    position = colname.replace('p', '').replace('_', ':')
    if position in SINGLE_POSITIONS:
      position_consensus = FEATURE_LABELS[consensus[colname]]
      plot_data[position] = {
        'consensus': position_consensus,
        'freqs': freqs[position]
      }
    if position in PAIRED_POSITIONS:
      position5, position3 = position.split(':')
      if consensus[colname] == '': 
        position5_consensus, position3_consensus = ('', '')
      else:
        position5_consensus, position3_consensus = FEATURE_LABELS[consensus[colname]]

      plot_data[position5] = {
        'consensus': position5_consensus,
        'freqs': freqs[position]
      }
      plot_data[position3] = {
        'consensus': position3_consensus,
        'freqs': freqs[position]
      }

  return JsonResponse(json.dumps(plot_data), safe = False)

def tilemap(request, clade):
  consensus_qs = models.Consensus.objects.filter(clade = clade).exclude(isotype = 'All')
  freqs_qs = models.Freq.objects.filter(clade = clade).exclude(isotype = 'All')
  plot_data = [] # use a list instead of dict - don't need to map positions to coords like for cloverleaf

  # preprocess freqs so Django doesn't submit separate queries per filter
  freqs = defaultdict(dict)
  for freq in freqs_qs.values():
    position = freq['position']
    isotype = freq['isotype']
    if position in SINGLE_POSITIONS:
      freqs[isotype][position] = {base: freq[base] for base in SINGLE_FEATURES}
    elif position in PAIRED_POSITIONS:
      freqs[isotype][position] = {PAIRED_FEATURES[pair]: freq[pair] for pair in PAIRED_FEATURES}

  consensus = consensus_qs.values()
  for consensus in consensus_qs.values():
    isotype = consensus['isotype']
    for colname in consensus:
      position = colname.replace('p', '').replace('_', ':')
      if position in SINGLE_POSITIONS:
        position_consensus = FEATURE_LABELS[consensus[colname]]
        plot_data.append({
          'position': position,
          'isotype': isotype,
          'consensus': position_consensus,
          'freqs': freqs[isotype][position],
          'type': 'single'
        })
      if position in PAIRED_POSITIONS:
        if consensus[colname] == '': 
          position5_consensus, position3_consensus = ('', '')
        else:
          position5_consensus, position3_consensus = FEATURE_LABELS[consensus[colname]]

        plot_data.append({
          'position': position,
          'isotype': isotype,
          'consensus': position5_consensus,
          'freqs': freqs[isotype][position],
          'type': 'left'
        })
        plot_data.append({
          'position': position,
          'isotype': isotype,
          'consensus': position3_consensus,
          'freqs': freqs[isotype][position],
          'type': 'right'
        })

  return JsonResponse(json.dumps(plot_data), safe = False)

def variation(request):
  filter_clades = {'8994': ('Saccharomyces', 'genus')}
  filter_isotypes = ['All']
  filter_positions = ['single']

  clade_list_qs = models.Consensus.objects.values('clade', 'rank').annotate(Max('id'))
  clade_list = {str(row['id__max']): (row['clade'], row['rank']) for row in clade_list_qs}

  if request.method == "POST":
    filter_clades = {str(row['id__max']): (row['clade'], row['rank']) for row in clade_list_qs.filter(id__max__in = request.POST.get('clades'))}
    filter_isotype = request.POST.get('isotypes')
    filter_positions = request.POST.get('positions')

  print(filter_isotypes)
  return render(request, 'explorer/variation.html', {
    'clades': filter_clades,
    'isotypes': filter_isotypes,
    'positions': filter_positions,
    'clade_list': clade_list
  })


def distribution(request, clades, isotypes, positions):
  pass

def compare(request):
  pass
