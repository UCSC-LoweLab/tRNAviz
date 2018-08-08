from django.shortcuts import render
from django.shortcuts import redirect
from django.db.models import Count, Max, Q
from django.core import serializers
from rest_framework.renderers import JSONRenderer
from collections import defaultdict
from django.http import JsonResponse
import json

from django_pandas.io import read_frame
import pandas as pd
from itertools import product

from . import models
from . import filters
from . import serializers



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
  '49:65', '50:64', '51:63', '52:62', '53:61'
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


def summary(request):
  filter_taxid = '4930'
  filter_clade = ('Saccharomyces', 'genus')
  filter_isotype = 'All'

  clade_dict = {}
  for taxonomy in models.Taxonomy.objects.values():
    clade_dict[taxonomy['taxid']] = taxonomy['name'], taxonomy['rank']

  if request.method == "POST":
    filter_taxid = request.POST.get('clade_txid')
    filter_clade = clade_dict[filter_taxid]
    filter_isotype = request.POST.get('isotype')

  return render(request, 'explorer/summary.html', {
    'clade': filter_clade,
    'clade_txid': filter_taxid,
    'isotype': filter_isotype,
    'clade_dict': clade_dict
  })

def variation_distribution(request):
  filter_clades = [{'4930': ('Saccharomyces', 'genus')}]
  filter_isotypes = ['All']
  filter_positions = ['single']

  clade_list = {}
  for taxonomy in models.Taxonomy.objects.values():
    clade_list[taxonomy['taxid']] = taxonomy['name'], taxonomy['rank']

  if request.method == "POST":
    clade_groups = [request.POST.getlist('form_clades_1'), request.POST.getlist('form_clades_2'), request.POST.getlist('form_clades_3'), request.POST.getlist('form_clades_4'), request.POST.getlist('form_clades_5')]
    filter_clades = []
    for clade_group in clade_groups:
      if len(clade_group) == 0: continue
      filter_clades.append({taxid: clade_list[taxid] for taxid in clade_group})
    filter_isotypes = request.POST.getlist('form_isotypes')
    filter_positions = request.POST.getlist('form_positions')

  return render(request, 'explorer/distribution.html', {
    'plot_clades': filter_clades,
    'isotypes': filter_isotypes,
    'positions': filter_positions,
    'clade_list': clade_list
  })

def variation_species(request):
  filter_clades = [{'4930': ('Saccharomyces', 'genus')}]
  foci = [[['Met'], ['54']], [['iMet'], ['54']], [['Met'], ['58']], [['iMet'], ['58']]]

  clade_list = {}
  for taxonomy in models.Taxonomy.objects.values():
    clade_list[taxonomy['taxid']] = taxonomy['name'], taxonomy['rank']

  if request.method == "POST":
    clade_groups = [request.POST.getlist('form_clades_1'), request.POST.getlist('form_clades_2'), request.POST.getlist('form_clades_3'), request.POST.getlist('form_clades_4'), request.POST.getlist('form_clades_5')]
    filter_clades = []
    for clade_group in clade_groups:
      if len(clade_group) == 0: continue
      filter_clades.append({taxid: clade_list[taxid] for taxid in clade_group})

    foci = [[[request.POST.get('form_isotypes_{}'.format(i))], [request.POST.get('form_positions_{}'.format(i))]] for i in range(1, 5)]
    for focus in foci:
      
  return render(request, 'explorer/species.html', {
    'plot_clades': filter_clades,
    'foci': foci,
    'clade_list': clade_list,
    'isotypes_list': ISOTYPES,
    'positions_list': SINGLE_POSITIONS + PAIRED_POSITIONS

  })

def get_coords(request):
  data = models.Coord.objects.all()
  serializer = serializers.CoordSerializer(data, many = True)
  return JsonResponse(serializer.data, safe = False)

def cloverleaf(request, clade_txid, isotype):
  consensus_qs = models.Consensus.objects.filter(taxid = clade_txid, isotype = isotype)
  freqs_qs = models.Freq.objects.filter(taxid = clade_txid, isotype = isotype)
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

def tilemap(request, clade_txid):
  consensus_qs = models.Consensus.objects.filter(taxid = clade_txid).exclude(isotype = 'All')
  freqs_qs = models.Freq.objects.filter(taxid = clade_txid).exclude(isotype = 'All')
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

def distribution(request, clade_txids, isotypes, positions):

  # reconstruct clade dict based on ids
  clade_groups = [[taxid for taxid in clade_group.split(',')] for clade_group in clade_txids.split(';')]
  clades = []
  for clade_group in clade_groups: clades.extend([taxid for taxid in clade_group])
  
  clade_info = {clade['taxid']: (clade['name'], clade['rank']) for clade in models.Taxonomy.objects.filter(taxid__in = clades).values()}
  isotypes = ISOTYPES if 'All' in isotypes else isotypes.split(',')

  if 'single' in positions:
    positions = SINGLE_POSITIONS
  elif 'paired' in positions:
    positions = PAIRED_POSITIONS
  query_positions = ['p{}'.format(position.replace(':', '_')) for position in positions]
  query_positions = query_positions + ['isotype']

  # Filter tRNA set with user queries
  # For filtering clades, the query is a series of or'd Q statements, e.g. Q('Genus' = 'Saccharomyces') 
  trnas = []
  for i, clade_group in enumerate(clade_groups):
    q_list = []
    for taxid in clade_info:
      if taxid not in clade_group: continue
      name, rank = clade_info[taxid]
      if rank == 'class':
        rank = 'taxclass'
      q_list.append(Q(**{str(rank): name}))
    query_filter_args = Q()
    for q in q_list:
      query_filter_args = query_filter_args | q
    trna_qs = models.tRNA.objects.filter(*(query_filter_args,)).filter(isotype__in = isotypes).values(*query_positions)
    df = read_frame(trna_qs)
    df['group'] = str(i + 1)
    trnas.append(df)
  trnas = pd.concat(trnas)
  freqs = trnas.groupby(['isotype', 'group']).apply(lambda position_counts: position_counts.drop(['isotype', 'group'], axis = 1).apply(lambda x: x.value_counts()).fillna(0))
  freqs = freqs.unstack(fill_value = 0).stack(0).reset_index().rename(columns = {'level_2': 'position'})
  freqs['position'] = freqs['position'].apply(lambda position: position[1:].replace('_', ':'))
  cols = ['isotype', 'position', 'group'] + ['A', 'C', 'G', 'U', '-'] + list(PAIRED_FEATURES.values())
  freqs = freqs.loc[:, freqs.columns.intersection(cols)]
  freqs = freqs.set_index(['isotype', 'position', 'group'], drop = False)

  # convert to d3-friendly format
  plot_data = defaultdict(dict)
  for isotype in freqs.index.levels[0]:
    for position in freqs.index.levels[1]:
      plot_data[isotype][position] = list(pd.DataFrame(freqs.loc[isotype, position]).to_dict(orient = 'index').values())

  return JsonResponse(json.dumps(plot_data), safe = False)


def species_distribution(request, clade_txids, foci):
  # reconstruct clade dict based on ids
  clade_groups = [[taxid for taxid in clade_group.split(',')] for clade_group in clade_txids.split(';')]
  clades = []
  for clade_group in clade_groups: clades.extend([taxid for taxid in clade_group])
  
  clade_info = {clade['taxid']: (clade['name'], clade['rank']) for clade in models.Taxonomy.objects.filter(taxid__in = clades).values()}
  foci = [tuple(focus.split(',')) for focus in foci.split(';')]
  isotypes = [isotype for isotype, position in foci]
  positions = [position for isotype, position in foci]
  print(positions)
  query_positions = ['p{}'.format(position.replace(':', '_')) for position in positions]
  query_positions = query_positions + ['isotype', 'assembly']

  # Filter tRNA set with user queries
  # For filtering clades, the query is a series of or'd Q statements, e.g. Q('Genus' = 'Saccharomyces') 
  trnas = []
  for i, clade_group in enumerate(clade_groups):
    q_list = []
    for taxid in clade_info:
      if taxid not in clade_group: continue
      name, rank = clade_info[taxid]
      if rank == 'class':
        rank = 'taxclass'
      q_list.append(Q(**{str(rank): name}))
    query_filter_args = Q()
    for q in q_list:
      query_filter_args = query_filter_args | q
    focus_filter_args = Q()
    trna_qs = models.tRNA.objects.filter(*(query_filter_args,)).filter(isotype__in = isotypes).values(*query_positions)
    df = read_frame(trna_qs)
    df['group'] = str(i + 1)
    trnas.append(df)
  trnas = pd.concat(trnas)
  freqs = trnas.groupby(['isotype', 'group', 'assembly']).apply(lambda position_counts: position_counts.drop(['isotype', 'group', 'assembly'], axis = 1).apply(lambda x: x.value_counts()).fillna(0))
  freqs = freqs.unstack(fill_value = 0).stack(0).reset_index().rename(columns = {'level_3': 'position'})
  freqs['position'] = freqs['position'].apply(lambda position: position[1:].replace('_', ':'))
  freqs['focus'] = freqs.apply(lambda row: '{}-{}'.format(row['isotype'], row['position']), axis = 1)
  freqs = freqs[freqs['focus'].isin(['{}-{}'.format(isotype, position) for isotype, position in zip(isotypes, positions)])]
  cols = ['focus', 'group', 'assembly'] + ['A', 'C', 'G', 'U', '-'] + list(PAIRED_FEATURES.values())
  freqs = freqs.loc[:, freqs.columns.intersection(cols)]
  freqs = freqs.set_index(['focus', 'group', 'assembly'], drop = False)

  # convert to d3-friendly format
  plot_data = defaultdict(dict)
  for focus in freqs.index.levels[0]:
    plot_data[focus] = list(pd.DataFrame(freqs.loc[focus]).to_dict(orient = 'index').values())

  return JsonResponse(json.dumps(plot_data), safe = False)

def compare(request):
  clade_list = {}
  for taxonomy in models.Taxonomy.objects.values():
    clade_list[taxonomy['taxid']] = taxonomy['name'], taxonomy['rank']

  return render(request, 'explorer/compare.html', {
    'clade_list': clade_list
  })

def render_bitchart(request):
  if request.method != "POST":
    return compare(request)

  return render(request, 'explorer/render-bitchart.html')