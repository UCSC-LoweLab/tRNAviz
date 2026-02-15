"""Shared constants and helpers for tRNAviz data loading."""

import time

# === Constants ===

RANKS = ['domain', 'kingdom', 'subkingdom', 'phylum', 'subphylum',
         'class', 'subclass', 'order', 'family', 'genus', 'species', 'assembly']

RANK_TO_FIELD = {r: ('taxclass' if r == 'class' else r) for r in RANKS}

SUMMARY_SINGLE_POSITIONS = [
  '8', '9', '14', '15', '16', '17', '17a', '18', '19', '20', '20a', '20b',
  '21', '26', '32', '33', '34', '35', '36', '37', '38', '44', '45', '46',
  '47', '48', '54', '55', '56', '57', '58', '59', '60', '73',
  'V1', 'V2', 'V3', 'V4', 'V5']

SUMMARY_PAIRED_POSITIONS = [
  '1:72', '2:71', '3:70', '4:69', '5:68', '6:67', '7:66',
  '10:25', '11:24', '12:23', '13:22',
  '27:43', '28:42', '29:41', '30:40', '31:39',
  '49:65', '50:64', '51:63', '52:62', '53:61',
  'V11:V21', 'V12:V22', 'V13:V23', 'V14:V24', 'V15:V25', 'V16:V26', 'V17:V27']

ISOTYPES = ['Ala', 'Arg', 'Asn', 'Asp', 'Cys', 'Gln', 'Glu', 'Gly', 'His',
            'Ile', 'Ile2', 'Leu', 'Lys', 'Met', 'Phe', 'Pro', 'Ser', 'Thr',
            'Trp', 'Tyr', 'Val', 'fMet', 'iMet']

SINGLE_FEATURES = ['A', 'C', 'G', 'U', '-']
PAIRED_FEATURE_MAP = {
  'A:U': 'AU', 'U:A': 'UA', 'G:C': 'GC', 'C:G': 'CG', 'G:U': 'GU', 'U:G': 'UG',
  '-:-': 'MM', 'A:A': 'AA', 'A:C': 'AC', 'A:G': 'AG', 'C:A': 'CA', 'C:C': 'CC',
  'C:U': 'CU', 'G:A': 'GA', 'G:G': 'GG', 'U:C': 'UC', 'U:U': 'UU',
  'A:-': 'AM', '-:A': 'MA', 'C:-': 'CM', '-:C': 'MC',
  'G:-': 'GM', '-:G': 'MG', 'U:-': 'UM', '-:U': 'MU',
}

# === Helpers ===

def pos_to_field(pos):
  """Convert position name like '1:72' to model field name like 'p1_72'."""
  return 'p' + pos.replace(':', '_')

def tsv_col_to_field(col):
  """Convert TSV column name to model field name."""
  if col == 'class': return 'taxclass'
  metadata = {'seqname', 'isotype', 'anticodon', 'score', 'primary', 'best_model',
    'isoscore', 'isoscore_ac', 'dbname', 'domain', 'kingdom', 'subkingdom',
    'phylum', 'subphylum', 'subclass', 'order', 'family', 'genus', 'species',
    'assembly', 'GCcontent', 'insertions', 'deletions', 'intron_length',
    'dloop', 'acloop', 'tpcloop', 'varm'}
  if col in metadata: return col
  return 'p' + col.replace(':', '_')

def fetch_ncbi_names(taxids):
  """Fetch taxon names from NCBI Entrez. Returns {taxid: name}."""
  names = {}
  try:
    from Bio import Entrez
    Entrez.email = 'tRNAviz@ucsc.edu'
    taxid_list = [str(t) for t in taxids if t]
    batch_size = 200
    for i in range(0, len(taxid_list), batch_size):
      batch = taxid_list[i:i+batch_size]
      try:
        handle = Entrez.efetch(db='taxonomy', id=batch, retmode='xml')
        records = Entrez.read(handle)
        handle.close()
        for record in records:
          names[record['TaxId']] = record['ScientificName']
        time.sleep(0.4)
      except Exception as e:
        print(f'    Warning: batch {i} failed: {e}')
      print(f'    Fetched {min(i+batch_size, len(taxid_list))}/{len(taxid_list)} names')
  except ImportError:
    print('    Biopython not available, skipping NCBI lookup')
  except Exception as e:
    print(f'    NCBI lookup error: {e}')
  return names


# === Consensus algorithms ===

def determine_single_consensus(counts, total, threshold):
  """Determine consensus code for a single position."""
  if total == 0:
    return None

  bases = {b: counts.get(b, 0) for b in ['A', 'C', 'G', 'U']}
  absent = counts.get('-', 0)

  if absent / total >= threshold:
    return 'Absent'

  sorted_b = sorted(bases.items(), key=lambda x: -x[1])

  # Single base
  for base, count in sorted_b:
    if count / total >= threshold:
      return base

  # Two-base combinations
  two_codes = {
    frozenset(['A', 'G']): 'Purine', frozenset(['C', 'U']): 'Pyrimidine',
    frozenset(['A', 'C']): 'Amino', frozenset(['G', 'U']): 'Keto',
    frozenset(['A', 'U']): 'Weak', frozenset(['C', 'G']): 'Strong',
  }
  top2 = frozenset([sorted_b[0][0], sorted_b[1][0]])
  if (sorted_b[0][1] + sorted_b[1][1]) / total >= threshold and top2 in two_codes:
    return two_codes[top2]

  # Three-base combinations
  three_codes = {
    frozenset(['C', 'G', 'U']): 'B', frozenset(['A', 'C', 'U']): 'H',
    frozenset(['A', 'G', 'U']): 'D', frozenset(['A', 'C', 'G']): 'V',
  }
  top3 = frozenset([sorted_b[0][0], sorted_b[1][0], sorted_b[2][0]])
  if (sorted_b[0][1] + sorted_b[1][1] + sorted_b[2][1]) / total >= threshold and top3 in three_codes:
    return three_codes[top3]

  return 'N'


def determine_paired_consensus(counts, total, threshold):
  """Determine consensus code for a paired position."""
  if total == 0:
    return None

  wc = {p: counts.get(p, 0) for p in ['A:U', 'U:A', 'G:C', 'C:G']}
  wb = {p: counts.get(p, 0) for p in ['G:U', 'U:G']}
  absent = counts.get('-:-', 0)

  if absent / total >= threshold:
    return 'Absent'

  # Individual pairs
  code_map = {'A:U': 'AU', 'U:A': 'UA', 'G:C': 'GC', 'C:G': 'CG',
              'G:U': 'GU', 'U:G': 'UG'}
  for pair in sorted(code_map.keys(), key=lambda p: -counts.get(p, 0)):
    if counts.get(pair, 0) / total >= threshold:
      return code_map[pair]

  # Combined pair categories
  combos = [
    (wc['G:C'] + wc['C:G'], 'StrongPair'),
    (wc['A:U'] + wc['U:A'], 'WeakPair'),
    (wb['G:U'] + wb['U:G'], 'WobblePair'),
    (wc['G:C'] + wc['A:U'], 'PurinePyrimidine'),
    (wc['C:G'] + wc['U:A'], 'PyrimidinePurine'),
    (wc['A:U'] + wc['C:G'], 'AminoKeto'),
    (wc['G:C'] + wc['U:A'], 'KetoAmino'),
  ]
  for count, code in sorted(combos, key=lambda x: -x[0]):
    if count / total >= threshold:
      return code

  total_paired = sum(wc.values()) + sum(wb.values())
  if total_paired / total >= threshold:
    return 'Paired'

  malformed_keys = ['A:-', '-:A', 'C:-', '-:C', 'G:-', '-:G', 'U:-', '-:U']
  if sum(counts.get(k, 0) for k in malformed_keys) / total >= threshold:
    return 'Malformed'

  mismatch_keys = ['A:A', 'A:C', 'A:G', 'C:A', 'C:C', 'C:U', 'G:A', 'G:G', 'U:C', 'U:U']
  if sum(counts.get(k, 0) for k in mismatch_keys) / total >= threshold:
    return 'Mismatched'

  # Default: check if paired dominates even below threshold
  if total_paired > 0 and total_paired >= sum(counts.get(k, 0) for k in mismatch_keys + malformed_keys + ['-:-']):
    return 'Paired'
  return 'NN'
