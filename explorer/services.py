from . import models
from . import serializers
from django.http import JsonResponse
import json
from collections import defaultdict

SINGLE_POSITIONS = ['8', '9', '14', '15', '16', '17', '17a', '18', '19', '20', '20a', '20b', '21', '26', 
'32', '33', '34', '35', '36', '37', '38', '44', '45', '46', '47', '48', '54', '55', '56', '57', '58', '59', '60', '73']
PAIRED_POSITIONS = ['1:72', '2:71', '3:70', '4:69', '5:68', '6:67', '7:66', '10:25', '11:24', '12:23', '13:22', 
  '27:43', '28:42', '29:41', '30:40', '31:39', '49:65', '50:64', '51:63', '52:62', '53:61']

SUMMARY_SINGLE_POSITIONS = SINGLE_POSITIONS + ['V1', 'V2', 'V3', 'V4', 'V5']
SUMMARY_PAIRED_POSITIONS = PAIRED_POSITIONS + ['V11:V21', 'V12:V22', 'V13:V23', 'V14:V24', 'V15:V25', 'V16:V26', 'V17:V27']
SUMMARY_SINGLE_FEATURES = {'A': 'A', 'C': 'C', 'G': 'G', 'U': 'U', 'absent': '-'}
SUMMARY_PAIRED_FEATURES = {
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
LABELS.update(SUMMARY_PAIRED_FEATURES)

SUMMARY_PAIRED_LABELS = {
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
      freqs[position] = {feature: freq[feature] for feature in SUMMARY_SINGLE_FEATURES}
    elif position in SUMMARY_PAIRED_POSITIONS:
      freqs[position] = {SUMMARY_PAIRED_FEATURES[pair]: freq[pair] for pair in SUMMARY_PAIRED_FEATURES}
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
        position5_consensus, position3_consensus = SUMMARY_PAIRED_LABELS[cons[colname]]

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
      freqs[isotype][position] = {base: freq[base] for base in SUMMARY_SINGLE_FEATURES}
    elif position in SUMMARY_PAIRED_POSITIONS:
      freqs[isotype][position] = {SUMMARY_PAIRED_FEATURES[pair]: freq[pair] for pair in SUMMARY_PAIRED_FEATURES}
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
          position5_consensus, position3_consensus = SUMMARY_PAIRED_LABELS[con[colname]]

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