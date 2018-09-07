from . import models
from . import serializers
from . import choices
from django.http import JsonResponse
import json
from collections import defaultdict
from django.db.models import Q
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
from django_pandas.io import read_frame

SINGLE_POSITIONS = ['8', '9', '14', '15', '16', '17', '17a', '18', '19', '20', '20a', '20b', '21', '26', 
'32', '33', '34', '35', '36', '37', '38', '44', '45', '46', '47', '48', '54', '55', '56', '57', '58', '59', '60', '73']
PAIRED_POSITIONS = ['1:72', '2:71', '3:70', '4:69', '5:68', '6:67', '7:66', '10:25', '11:24', '12:23', '13:22', 
  '27:43', '28:42', '29:41', '30:40', '31:39', '49:65', '50:64', '51:63', '52:62', '53:61']

SUMMARY_SINGLE_POSITIONS = SINGLE_POSITIONS + ['V1', 'V2', 'V3', 'V4', 'V5']
SUMMARY_PAIRED_POSITIONS = PAIRED_POSITIONS + ['V11:V21', 'V12:V22', 'V13:V23', 'V14:V24', 'V15:V25', 'V16:V26', 'V17:V27']
SINGLE_FEATURES = {'A': 'A', 'C': 'C', 'G': 'G', 'U': 'U', 'absent': '-'}
PAIRED_FEATURES = {
  'AU': 'A:U', 'UA': 'U:A', 'GC': 'G:C', 'CG': 'C:G', 'GU': 'G:U', 'UG': 'U:G', 
  'AA': 'A:A', 'AC': 'A:C', 'AG': 'A:G', 'CA': 'C:A', 'CC': 'C:C', 'CU': 'C:U', 'GA': 'G:A', 'GG': 'G:G', 'UC': 'U:C', 'UU': 'U:U',
  'AM': 'A:-', 'CM': 'C:-', 'GM': 'G:-', 'UM': 'U:-', 'MA': '-:A', 'MC': '-:C', 'MG': '-:G', 'MU': '-:U', 'MM': '-:-'
}

LABELS = {
  'A': 'A', 'G': 'G', 'C': 'C', 'U': 'U', 'Absent': '-', '': '',  'Purine': 'Purine', 'Pyrimidine': 'Pyrimidine',
  'Amino': 'A / C', 'Keto': 'G / U', 'Weak': 'A / U', 'Strong': 'G / C', 
  'B': 'C / G / U', 'H': 'A / C / U', 'D': 'A / G / U', 'V': 'A / C / G', 'N': 'N',
  'PurinePyrimidine': 'Purine:Pyrimidine', 'PyrimidinePurine': 'Pyrimidine:Purine',
  'WobblePair': 'G:U / U:G', 'StrongPair': 'G:C / C:G', 'WeakPair': 'A:U / U:A', 'AminoKeto': 'A:U / C:G', 'KetoAmino': 'G:C / U:A', 
  'Paired': 'Paired', 'Bulge': '-:N / N:-', 'Mismatched': 'Mismatched', 'NN': 'N:N'
}
LABELS.update(PAIRED_FEATURES)

CONSENSUS_PAIRED_LABELS = {
  'GC': ('G', 'C'), 'AU': ('A', 'U'), 'UA': ('U', 'A'), 'CG': ('C', 'G'), 'GU': ('G', 'U'), 'UG': ('U', 'G'),
  'PurinePyrimidine': ('Purine', 'Pyrimidine'), 'PyrimidinePurine': ('Pyrimidine', 'Purine'), 'WobblePair': ('G / U', 'G / U'),
  'StrongPair': ('G / C', 'G / C'), 'WeakPair': ('A / U', 'A / U'), 'AminoKeto': ('A / C', 'G / U'), 'KetoAmino': ('G / U', 'A / C'),
  'Paired': ('Paired', 'Paired'), 'Bulge': ('Bulge', 'Bulge'), 'Mismatched': ('Mismatched', 'Mismatched'), 'NN': ('N', 'N')
}


def get_coords(request):
  data = models.Coord.objects.all()
  serializer = serializers.CoordSerializer(data, many = True)
  return JsonResponse(serializer.data, safe = False)

def gather_cloverleaf_freqs(clade_txid, isotype):
  freqs_qs = models.Freq.objects.filter(taxid = clade_txid, isotype = isotype)
  # preprocess freqs so Django doesn't submit separate queries per filter
  freqs = {}
  for freq in freqs_qs.values():
    position = freq['position']
    if position in SUMMARY_SINGLE_POSITIONS:
      freqs[position] = {feature: freq[feature] for feature in SINGLE_FEATURES}
    elif position in SUMMARY_PAIRED_POSITIONS:
      freqs[position] = {PAIRED_FEATURES[pair]: freq[pair] for pair in PAIRED_FEATURES}
  return freqs

def annotate_cloverleaf_positions(cons, freqs):
  # create 95 dicts, one for each position, each containing a freqs dict and consensus feature
  plot_data = {}
  for colname in cons:
    position = colname.replace('p', '').replace('_', ':')
    if position in SUMMARY_SINGLE_POSITIONS:
      position_consensus = LABELS[cons[colname]]
      plot_data[position] = {
        'consensus': position_consensus,
        'freqs': freqs[position]
      }
    elif position in SUMMARY_PAIRED_POSITIONS:
      position5, position3 = position.split(':')
      if cons[colname] == '': 
        position5_consensus, position3_consensus = ('', '')
      else:
        position5_consensus, position3_consensus = CONSENSUS_PAIRED_LABELS[cons[colname]]

      plot_data[position5] = {
        'consensus': position5_consensus,
        'freqs': freqs[position]
      }
      plot_data[position3] = {
        'consensus': position3_consensus,
        'freqs': freqs[position]
      }
  return plot_data

def cloverleaf(request, clade_txid, isotype):
  cons_qs = models.Consensus.objects.filter(taxid = clade_txid, isotype = isotype)
  cons = cons_qs.values()[0]
  freqs = gather_cloverleaf_freqs(clade_txid, isotype)
  plot_data = annotate_cloverleaf_positions(cons, freqs)
  return JsonResponse(plot_data)

def gather_tilemap_freqs(clade_txid):
  freqs_qs = models.Freq.objects.filter(taxid = clade_txid).exclude(isotype = 'All')
  # preprocess freqs so Django doesn't submit separate queries per filter
  freqs = defaultdict(dict)
  for freq in freqs_qs.values():
    position = freq['position']
    isotype = freq['isotype']
    if position in SUMMARY_SINGLE_POSITIONS:
      freqs[isotype][position] = {base: freq[base] for base in SINGLE_FEATURES}
    elif position in SUMMARY_PAIRED_POSITIONS:
      freqs[isotype][position] = {PAIRED_FEATURES[pair]: freq[pair] for pair in PAIRED_FEATURES}
  return freqs

def annotate_tiles(cons, freqs):
  plot_data = [] # use a list instead of dict - don't need to map positions to coords like for cloverleaf
  for con in cons:
    isotype = con['isotype']
    for colname in con:
      position = colname.replace('p', '').replace('_', ':')
      if position in SUMMARY_SINGLE_POSITIONS:
        position_consensus = LABELS[con[colname]]
        plot_data.append({
          'position': position,
          'isotype': isotype,
          'consensus': position_consensus,
          'freqs': freqs[isotype][position],
          'type': 'single'
        })
      if position in SUMMARY_PAIRED_POSITIONS:
        if con[colname] == '': 
          position5_consensus, position3_consensus = ('', '')
        else:
          position5_consensus, position3_consensus = CONSENSUS_PAIRED_LABELS[con[colname]]

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
  return plot_data

def tilemap(request, clade_txid):
  cons_qs = models.Consensus.objects.filter(taxid = clade_txid).exclude(isotype = 'All')
  cons = cons_qs.values()
  freqs = gather_tilemap_freqs(clade_txid)
  plot_data = annotate_tiles(cons, freqs)
  return JsonResponse(plot_data, safe = False)

def reconstruct_clade_group_info(clade_txids):
  clade_groups = [[txid for txid in clade_group.split(',')] for clade_group in clade_txids.split(';')]
  all_clades = []
  for clade_group in clade_groups: all_clades.extend([txid for txid in clade_group])
  clade_info = {taxid: (clade.rsplit(' ', 1)[0], clade.rsplit(' ', 1)[1][1:-1]) for taxid, clade in choices.CLADES if taxid in all_clades}
  return clade_groups, clade_info

def position_sort_key(position):
  if 'V' not in position:
    if 'a' in position: return 20.1
    elif 'b' in position: return 20.2
    else: return int(position.split(':')[0])
  else: return int(position[1:].split(':')[0]) * 0.1 + 45

def uniquify_positions(positions):
  positions = positions.split(',')
  query_positions = []
  if 'single' in positions:
    query_positions.extend([y for x, y in choices.SINGLE_POSITIONS])
    query_positions.remove('Single positions')
    positions.remove('single')
  if 'paired' in positions:
    query_positions.extend([y for x, y in choices.PAIRED_POSITIONS])
    query_positions.remove('Paired positions')
    positions.remove('paired')
  if 'tertiary' in positions:
    query_positions.extend([y for x, y in choices.TERTIARY_INTERACTIONS])
    query_positions.remove('Tertiary interactions')
    positions.remove('tertiary')
  if 'variable' in positions:
    query_positions.extend([y for x, y in choices.VARIABLE_ARM])
    query_positions.remove('Variable arm')
    positions.remove('variable')
  query_positions.extend(positions)
  # rough position sort
  query_positions = sorted(list(set(query_positions)), key = position_sort_key)
  return query_positions

def query_trnas_for_distribution(clade_groups, clade_info, isotypes, positions):
  # Filter tRNA set with user queries
  trnas = []
  for i, clade_group in enumerate(clade_groups):
    # For filtering clades, the query is a series of or'd Q statements, e.g. Q('genus' = 'Saccharomyces') 
    q_list = []
    for taxid in clade_info:
      if taxid not in clade_group: continue
      name, rank = clade_info[taxid]
      if rank == 'class': rank = 'taxclass'
      q_list.append(Q(**{str(rank): name}))
    query_filter_args = Q()
    for q in q_list:
      query_filter_args = query_filter_args | q

    trna_qs = models.tRNA.objects.filter(*(query_filter_args,)).filter(isotype__in = isotypes).values(*positions)
    df = read_frame(trna_qs)
    df['group'] = str(i + 1)
    trnas.append(df)

  return pd.concat(trnas)
  
def convert_trnas_to_freqs_df(trnas):
  freqs = trnas.groupby(['isotype', 'group']).apply(lambda position_counts: position_counts.drop(['isotype', 'group'], axis = 1).apply(lambda x: x.value_counts()).fillna(0))
  freqs = freqs.unstack(fill_value = 0).stack(0).reset_index().rename(columns = {'level_2': 'position'})
  freqs['position'] = freqs['position'].apply(lambda position: position[1:].replace('_', ':'))
  cols = ['isotype', 'position', 'group'] + ['A', 'C', 'G', 'U', '-'] + list(PAIRED_FEATURES.values())
  freqs = freqs.loc[:, freqs.columns.intersection(cols)]
  freqs = freqs.set_index(['isotype', 'position', 'group'], drop = False)
  return freqs

def convert_freqs_to_dict(freqs):
  # convert to d3-friendly format
  plot_data = defaultdict(dict)
  for isotype in freqs.index.levels[0]:
    for position in freqs.index.levels[1]:
      plot_data[isotype][position] = list(pd.DataFrame(freqs.loc[isotype, position]).to_dict(orient = 'index').values())
  return plot_data

def distribution(request, clade_txids, isotypes, positions):
  clade_groups, clade_info = reconstruct_clade_group_info(clade_txids)
  isotypes = [x for x, y in choices.ISOTYPES] if 'All' in isotypes else isotypes.split(',')
  # Format positions into column names
  positions = uniquify_positions(positions)
  query_positions = ['p{}'.format(position.replace(':', '_')) for position in positions] + ['isotype']
  
  trnas = query_trnas_for_distribution(clade_groups, clade_info, isotypes, query_positions)
  freqs = convert_trnas_to_freqs_df(trnas)
  plot_data = convert_freqs_to_dict(freqs)
  return JsonResponse(plot_data)

def species_convert_trnas_to_freqs_df(trnas, isotypes, positions):
  freqs = trnas.groupby(['isotype', 'group', 'assembly']).apply(lambda position_counts: position_counts.drop(['isotype', 'group', 'assembly'], axis = 1).apply(lambda x: x.value_counts()).fillna(0))
  freqs = freqs.unstack(fill_value = 0).stack(0).reset_index().rename(columns = {'level_3': 'position'})
  freqs['position'] = freqs['position'].apply(lambda position: position[1:].replace('_', ':'))
  freqs['focus'] = freqs.apply(lambda row: '{}-{}'.format(row['isotype'], row['position']), axis = 1)
  freqs = freqs[freqs['focus'].isin(['{}-{}'.format(isotype, position) for isotype, position in zip(isotypes, positions)])]
  cols = ['focus', 'group', 'assembly'] + ['A', 'C', 'G', 'U', '-'] + list(PAIRED_FEATURES.values())
  freqs = freqs.loc[:, freqs.columns.intersection(cols)]
  freqs = freqs.set_index(['focus', 'group', 'assembly'], drop = False)
  return freqs

def species_distribution(request, clade_txids, foci):
  clade_groups, clade_info = reconstruct_clade_group_info(clade_txids)
  foci = [tuple(focus.split(',')) for focus in foci.split(';')]
  isotypes, positions = zip(*foci)
  positions = [position for isotype, position in foci]
  query_positions = ['p{}'.format(position.replace(':', '_')) for position in positions] + ['isotype', 'assembly']
  trnas = query_trnas_for_distribution(clade_groups, clade_info, isotypes, query_positions)
  freqs = species_convert_trnas_to_freqs_df(trnas, isotypes, positions)

  # convert to d3-friendly format
  plot_data = defaultdict(dict)
  for focus in freqs.index.levels[0]:
    plot_data[focus] = list(pd.DataFrame(freqs.loc[focus]).to_dict(orient = 'index').values())

  return JsonResponse(plot_data, safe = True)

