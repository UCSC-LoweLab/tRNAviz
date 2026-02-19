#!/usr/bin/env python
import sys, os
message = lambda s: print(s, file = sys.stderr, end = '', flush = True)
message('Loading packages...')
import pandas as pd
import numpy
import argparse
import datetime
import re
from collections import OrderedDict
message('done\n')

def main():
  # Read in tRNAs

  message('Loading tRNAs from {}...'.format(input_tRNAs))
  trnas = pd.read_csv(input_tRNAs, sep = '\t', dtype = {
    'seqname': str,
    'isotype': str,
    'anticodon': str,
    'score': float,
    'primary': bool,
    'best_model': str,
    'isoscore': float,
    'isoscore_ac': float,
    'dbname': str,
    'domain': str,
    'kingdom': str,
    'subkingdom': str,
    'phylum': str,
    'subphylum': str,
    'class': str,
    'subclass': str,
    'order': str,
    'family': str,
    'genus': str,
    'species': str,
    'assembly': str,
    'GCcontent': float,
    'insertions': int,
    'deletions': int,
    'intron_length': int,
    'dloop': int,
    'acloop': int,
    'tpcloop': int,
    'varm': int
  })
  trnas = trnas[trnas.isotype.isin(isotypes) & trnas.primary]
  message('done\n')

  message('Parsing clades and taxonomic ranks...')
  taxonomy = pd.read_csv(taxonomy_file, sep = '\t', dtype = {'name': str, 'rank': str, 'taxid': str})
  message('done\n')

  message('Calculating consensus features for {} clades...\n'.format(taxonomy[taxonomy['rank'] != 'assembly'].shape[0]))
  if saved and os.path.exists('consensus-saved.pkl'):
    message('\tLoading saved data...')
    consensus = pd.read_pickle('consensus-saved.pkl')
    if (consensus.size == 0): 
      message('found empty consensus file, did not load data\n')
      consensus = pd.DataFrame()
    else: message('done\n')
  else:
    consensus = pd.DataFrame()
  for name, rank, taxid in taxonomy[['name', 'rank', 'taxid']].itertuples(index = False):
    if rank == 'assembly': continue
    try:
      message('\tResolving consensus for {} ({})...'.format(name, rank))
      if saved and 'taxid' in consensus.columns and not consensus[(consensus['taxid'] == taxid)].empty:
        message('using saved data from previous run\n')
        continue
      current_clade_trnas = trnas[trnas[rank] == taxid]
      current_clade_consensus = resolve_consensus_isotypes(current_clade_trnas)
      current_clade_consensus['taxid'] = taxid
      consensus = consensus.append(current_clade_consensus, sort = True)
      message('done\n')
    except Exception as e:
      if saved: consensus.to_pickle('consensus-saved.pkl')
      raise e
    # save after each record
    if saved:
      consensus.to_pickle('consensus-saved.pkl')
  message('Done\n')
  
  message('Exporting results to {}...'.format(output_file))
  consensus = consensus.set_index(['taxid', 'isotype', 'position', 'type']).unstack('position')
  consensus.columns = consensus.columns.get_level_values(1)
  # Make sure all positions are included even if no consensus is found
  consensus = consensus.append(pd.DataFrame(columns = list(positions.values())), sort = True).fillna('')
  consensus = consensus[list(positions.values())]
  consensus.to_csv(path_or_buf = output_file, sep = '\t')
  message('done\n')


def resolve_consensus_isotypes(trnas):
  '''Resolve consensus features across all isotypes given a set of tRNAs'''
  consensus = resolve_consensus(trnas)
  consensus['isotype'] = 'All'

  for isotype in isotypes:
    current_isotype_trnas = trnas.loc[trnas.isotype == isotype]
    if current_isotype_trnas.shape[0] == 0:
      continue
    current_isotype_consensus = resolve_consensus(current_isotype_trnas)
    current_isotype_consensus['isotype'] = isotype
    consensus = consensus.append(current_isotype_consensus, sort = True)
  return(consensus)

def resolve_consensus(trnas):
  '''Resolve consensus features across positions given a set of tRNAs'''
  consensus = [] # to be converted into a pandas dataframe later

  for position in positions:
    current_position = {'position': positions[position]}
    freqs = trnas.loc[:, positions[position]].where(lambda x: x.isin(features)).value_counts(normalize = True)
    candidate_features = get_candidate_features(freqs.keys(), combos)

    # Find the first candidate feature that passes all checks and add to dataframe
    for candidate in candidate_features:
      freq_check = freqs[freqs.index.isin(combos[candidate]) & (freqs >= 0.05)].sum() > 0.9
      if not freq_check:
        continue
      species_check = True
      for isotype in trnas.isotype.where(trnas.isotype.isin(isotypes)).unique():
        current_isotype_trnas = trnas.loc[trnas.isotype == isotype]
        current_isotype_freqs = current_isotype_trnas.loc[:, positions[position]].where(lambda x: x.isin(features)).value_counts(normalize = True)
        freq_check = freq_check & (current_isotype_freqs[current_isotype_freqs.index.isin(combos[candidate]) & (current_isotype_freqs >= 0.05)].sum() > 0.9)

        species_check = species_check & (all(
          current_isotype_trnas.loc[:, [positions[position], 'species']].groupby(
            'species', group_keys = False
          ).apply(
            lambda subset, position, combo: any(subset.loc[:, position].isin(combo)), 
            position = positions[position],
            combo = combos[candidate]
          ))
        )
      if species_check and freq_check:
        current_position['feature'] = candidate
        current_position['type'] = 'Consensus'
        consensus.append(current_position.copy())
        break

    # Find the first high frequency feature for "near consensus" features
    for candidate in candidate_features:
      freq_check = freqs[freqs.index.isin(combos[candidate]) & (freqs >= 0.05)].sum() > 0.9
      if freq_check:
        # Add a new row for near-consensus unless it's the same as the consensus feature
        if 'feature' in current_position and current_position['feature'] == candidate:
          break
        current_position['feature'] = candidate
        current_position['type'] = 'Near-consensus'
        consensus.append(current_position)
        break
      # High mismatch rate positions don't need a 5% inclusion rate, 90% threshold, or species check
      elif candidate == 'Mismatched':
        if freqs[freqs.index.isin(combos[candidate])].sum() > 0.7:
          current_position['feature'] = 'High mismatch rate'
          current_position['type'] = 'Near-consensus'

  return pd.DataFrame(consensus)

def get_candidate_features(features, combos):
  candidates = []
  for combo in combos: #  e.g., ('A', 'G')
    # current combo is a candidate feature if each letter in the combo exists in the feature set
    if numpy.any(numpy.isin(combos[combo], features)):
      candidates.append(combo)
  return candidates

def parse_args():
  parser = argparse.ArgumentParser(description = "Generate table of tRNA features using tRNAscan-SE output")
  parser.add_argument('-t', '--input_tRNAs', default = 'tRNAs.tsv', help = '')
  parser.add_argument('-c', '--taxonomy', default = 'taxonomy.tsv', help = '')
  parser.add_argument('-o', '--output_file', default = 'consensus-{}.tsv'.format(timestamp), help = '')
  parser.add_argument('-s', '--saved', default = False, action = 'store_true', help = 'Use and save data before/after a failed run')
  return parser.parse_args()


if __name__ == '__main__':
  timestamp = '{:%m%d%y-%H%M%S}'.format(datetime.datetime.now())
  args = parse_args()
  input_tRNAs = args.input_tRNAs
  output_file = args.output_file
  taxonomy_file = args.taxonomy
  saved = args.saved

  isotypes = ['Ala', 'Arg', 'Asn', 'Asp', 'Cys', 'Gln', 'Glu', 'Gly', 'His', 'Ile',  'Ile2', 'fMet', 'iMet', 'Leu', 'Lys', 'Met', 'Phe', 'Pro', 'Ser', 'Thr', 'Trp', 'Tyr', 'Val']
  positions = [('p1_72', '1:72'), ('p1', '1'), ('p2_71', '2:71'), ('p2', '2'), ('p3_70', '3:70'), ('p3', '3'), ('p4_69', '4:69'), ('p4', '4'), ('p5_68', '5:68'), ('p5', '5'), ('p6_67', '6:67'), ('p6', '6'), ('p7_66', '7:66'), ('p7', '7'), ('p8', '8'), ('p8_14', '8:14'), ('p9', '9'), ('p9_23', '9:23'), ('p10_25', '10:25'), ('p10', '10'), ('p10_45', '10:45'), ('p11_24', '11:24'), ('p11', '11'), ('p12_23', '12:23'), ('p12', '12'), ('p13_22', '13:22'), ('p13', '13'), ('p14', '14'), ('p15', '15'), ('p15_48', '15:48'), ('p16', '16'), ('p17', '17'), ('p17a', '17a'), ('p18', '18'), ('p18_55', '18:55'), ('p19', '19'), ('p19_56', '19:56'), ('p20', '20'), ('p20a', '20a'), ('p20b', '20b'), ('p21', '21'), ('p22', '22'), ('p22_46', '22:46'), ('p23', '23'), ('p24', '24'), ('p25', '25'), ('p26', '26'), ('p26_44', '26:44'), ('p27_43', '27:43'), ('p27', '27'), ('p28_42', '28:42'), ('p28', '28'), ('p29_41', '29:41'), ('p29', '29'), ('p30_40', '30:40'), ('p30', '30'), ('p31_39', '31:39'), ('p31', '31'), ('p32', '32'), ('p33', '33'), ('p34', '34'), ('p35', '35'), ('p36', '36'), ('p37', '37'), ('p38', '38'), ('p39', '39'), ('p40', '40'), ('p41', '41'), ('p42', '42'), ('p43', '43'), ('p44', '44'), ('p45', '45'), ('pV11_V21', 'V11:V21'), ('pV12_V22', 'V12:V22'), ('pV13_V23', 'V13:V23'), ('pV14_V24', 'V14:V24'), ('pV15_V25', 'V15:V25'), ('pV16_V26', 'V16:V26'), ('pV17_V27', 'V17:V27'), ('pV1', 'V1'), ('pV2', 'V2'), ('pV3', 'V3'), ('pV4', 'V4'), ('pV5', 'V5'), ('pV11', 'V11'), ('pV12', 'V12'), ('pV13', 'V13'), ('pV14', 'V14'), ('pV15', 'V15'), ('pV16', 'V16'), ('pV17', 'V17'), ('pV21', 'V21'), ('pV22', 'V22'), ('pV23', 'V23'), ('pV24', 'V24'), ('pV25', 'V25'), ('pV26', 'V26'), ('pV27', 'V27'), ('p46', '46'), ('p47', '47'), ('p48', '48'), ('p49_65', '49:65'), ('p49', '49'), ('p50_64', '50:64'), ('p50', '50'), ('p51_63', '51:63'), ('p51', '51'), ('p52_62', '52:62'), ('p52', '52'), ('p53_61', '53:61'), ('p53', '53'), ('p54', '54'), ('p54_58', '54:58'), ('p55', '55'), ('p56', '56'), ('p57', '57'), ('p58', '58'), ('p59', '59'), ('p60', '60'), ('p61', '61'), ('p62', '62'), ('p63', '63'), ('p64', '64'), ('p65', '65'), ('p66', '66'), ('p67', '67'), ('p68', '68'), ('p69', '69'), ('p70', '70'), ('p71', '71'), ('p72', '72'), ('p73', '73')]
  positions = OrderedDict(positions)
  combos = [('A', ('A',)), ('C', ('C',)), ('G', ('G',)), ('U', ('U',)), ('Absent', ("-", "-:-")), 
    ('GC', ("G:C",)), ('AU', ("A:U",)), ('UA', ("U:A",)), ('CG', ("C:G",)), ('GU', ("G:U",)), ('UG', ("U:G",)), 
    ('Purine', ("A", "G")), ('Pyrimidine', ("C", "U")), ('StrongPair', ("G:C", "C:G")), 
    ('WeakPair', ("A:U", "U:A")), ('WobblePair', ("G:U", "U:G")),
    ('Weak', ("A", "U")), ('Strong', ("G", "C")), 
    ('Amino', ("A", "C")), ('Keto', ("G", "U")), 
    ('PurinePyrimidine', ("A:U", "G:C")), ('PyrimidinePurine', ("U:A", "C:G")),
    ('AminoKeto', ('A:U', 'C:G')), ('KetoAmino', ('U:A', 'G:C')), 
    ('B', ("C", "G", "U")), ('D', ("A", "G", "U")), ('H', ("A", "C", "U")), ('V', ("A", "C", "G")), 
    ('Paired', ("A:U", "U:A", "C:G", "G:C", "G:U", "U:G")), 
    ('Mismatched', ("A:A", "G:G", "C:C", "U:U", "A:G", "A:C", "C:A", "C:U", "G:A", "U:C")), 
    ('Malformed', ("A:-", "U:-", "C:-", "G:-", "-:A", "-:G", "-:C", "-:U"))]
  combos = OrderedDict(combos)
  features = [feature for combo in combos.values() for feature in combo]
  main()
