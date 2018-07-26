from django.shortcuts import render
from django.shortcuts import redirect
from django.db.models import Count, Max, Q
from django.core import serializers
from rest_framework.renderers import JSONRenderer
from collections import defaultdict
from django.http import JsonResponse
import json

from django_pandas.io import read_frame
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

def variation(request):
  filter_clades = {'4895': ('Saccharomyces', 'genus')}
  filter_isotypes = ['All']
  filter_positions = ['single']

  clade_list = {}
  for taxonomy in models.Taxonomy.objects.values():
    clade_list[taxonomy['taxid']] = taxonomy['name'], taxonomy['rank']

  if request.method == "POST":
    filter_clades = {taxid: clade_list[taxid] for taxid in request.POST.getlist('clades')}
    filter_isotype = request.POST.getlist('isotypes')
    filter_positions = request.POST.getlist('positions')

  return render(request, 'explorer/variation.html', {
    'clades': filter_clades,
    'isotypes': filter_isotypes,
    'positions': filter_positions,
    'clade_list': clade_list
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

def distribution(request, clades, isotypes, positions):
  # reconstruct clade dict based on ids
  clades = [int(taxid) for taxid in clades.split(',')]
  groups = 1
  clade_list = [(clade['name'], clade['rank']) for clade in models.Taxonomy.objects.filter(taxid__in = clades).values()]

  print(clades)
  # print(models.Taxonomy.objects.filter(taxid__in = clades))

  isotypes = ISOTYPES if 'All' in isotypes else isotypes

  if 'single' in positions:
    positions = SINGLE_POSITIONS
  elif 'paired' in positions:
    positions = PAIRED_POSITIONS
  query_positions = ['p{}'.format(position.replace(':', '_')) for position in positions]
  query_positions = query_positions + ['isotype']

  # Filter tRNA set with user query
  # For filtering clades, the query is a series of or'd Q statements, e.g. Q('Genus' = 'Saccharomyces') 
  q_list = [Q(**{str(rank): name}) for name, rank in clade_list]
  query_filter_args = Q()
  for q in q_list:
    query_filter_args = query_filter_args | q
  trna_qs = models.tRNA.objects.filter(*(query_filter_args,)).filter(isotype__in = isotypes).values(*query_positions)
  
  # migrate to pandas to count freqs and munge
  trnas = read_frame(trna_qs)
  trnas = trnas.groupby('isotype').apply(lambda position_counts: position_counts.drop('isotype', axis = 1).apply(lambda x: x.value_counts()).fillna(0))
  freqs = trnas.unstack().stack(0)
  freqs.index = freqs.index.rename(['isotype', 'position']).set_levels(level = 'position', levels = freqs.index.levels[1].map(lambda x: x[1:].replace('_', ':')))

  # plot_data = {}
  # for isotype in freqs.index.levels[0]:
  #   # dict is { isotype : { position : { base: freq, base2: freq}}}
  #   # example: 'Thr': {'20': {'U': 57.0, 'G': 0.0, 'A': 0.0, 'C': 0.0, '-': 0.0}
  #   plot_data[isotype] = freqs.loc[isotype].to_dict(orient = 'index')
  # return JsonResponse(json.dumps(plot_data), safe = False)

  freqs = freqs.reset_index().set_index(['isotype', 'position'], drop = False)
  plot_data = defaultdict(dict)
  for isotype in freqs.index.levels[0]:
    for position in freqs.index.levels[1]:
      if groups == 1:
        plot_data[isotype][position] = [freqs.loc[isotype, position].to_dict()]
        # '17': [{'position': '17', 'isotype': 'Ala', 'A': 0, 'U': 34, ...}], '17a': [...]
      else:
        plot_data[isotype][position] = list(pd.DataFrame(freqs.loc[isotype, position]).to_dict().values())
      # [{'position': '17', 'isotype': 'Ala', 'A': 0, 'U': 34, ...}, {'position': '17', ...}]

  # freqs = freqs.rename(columns = {'level_1': 'position'})
  # freqs['position'] = freqs['position'].apply(lambda x: x[1:].replace('_', ':'))

  # plot_data = list(freqs.head().T.to_dict().values())
  return JsonResponse(json.dumps(plot_data), safe = False)

def compare(request):
  pass
