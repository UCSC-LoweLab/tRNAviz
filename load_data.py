#!/usr/bin/env python
"""Load tRNAviz data into Django database from TSV files.

Usage: python load_data.py
"""

import os, sys, csv, time, math
from collections import defaultdict, Counter

# Setup Django
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tRNAviz.settings')
sys.path.insert(0, BASE_DIR)

import django
django.setup()

from django.db import connection
from explorer.models import Taxonomy, tRNA as tRNAModel, Consensus, Freq, Coord
from explorer.load_utils import (
    RANKS, RANK_TO_FIELD, ISOTYPES, SUMMARY_SINGLE_POSITIONS, SUMMARY_PAIRED_POSITIONS,
    SINGLE_FEATURES, PAIRED_FEATURE_MAP,
    pos_to_field, tsv_col_to_field, fetch_ncbi_names,
    determine_single_consensus, determine_paired_consensus,
)

# === Constants ===

DATA_DIRS = {
  'archaea': {
    'genomes': os.path.join(BASE_DIR, 'archaea', 'genomes.tsv'),
    'trnas': os.path.join(BASE_DIR, 'archaea', 'tRNAs-111618-112435.tsv'),
  },
  'bacteria': {
    'genomes': os.path.join(BASE_DIR, 'bacteria', 'genomes.tsv'),
    'trnas': os.path.join(BASE_DIR, 'bacteria', 'tRNAs-111618-112536.tsv'),
  },
  'eukaryotes': {
    'genomes': os.path.join(BASE_DIR, 'eukaryotes', 'genomes.tsv'),
    'trnas': os.path.join(BASE_DIR, 'eukaryotes', 'tRNAs-111618-112505.tsv'),
  },
}


# === Step 1: Load Taxonomy ===

def load_taxonomy():
  print('\n=== Step 1: Loading Taxonomy ===')

  # Collect unique taxa: taxid -> {rank, lineage, name}
  taxon_info = {}
  assembly_names = {}

  for dname, files in DATA_DIRS.items():
    print(f'  Reading {dname}/genomes.tsv ...')
    with open(files['genomes'], 'r') as f:
      reader = csv.DictReader(f, delimiter='\t')
      for row in reader:
        # For each rank level, extract the taxid and lineage
        for rank in RANKS:
          taxid = row.get(rank, '').strip()
          if not taxid or taxid in taxon_info:
            continue

          # Build lineage up to this rank
          lineage = {}
          for r in RANKS:
            field = RANK_TO_FIELD[r]
            val = row.get(r, '').strip()
            lineage[field] = val if val else None
            if r == rank:
              break
          # Null out ranks below this one
          below = False
          for r in RANKS:
            if below:
              lineage[RANK_TO_FIELD[r]] = None
            if r == rank:
              below = True

          taxon_info[taxid] = {'rank': rank, 'lineage': lineage}

          if rank == 'assembly':
            assembly_names[taxid] = row['name']

  print(f'  Found {len(taxon_info)} unique taxa')

  # Fetch names from NCBI for non-assembly taxa
  need_names = [tid for tid, d in taxon_info.items() if d['rank'] != 'assembly']
  print(f'  Looking up {len(need_names)} non-assembly taxon names from NCBI...')
  ncbi_names = fetch_ncbi_names(need_names)

  # Create Taxonomy objects
  Taxonomy.objects.all().delete()
  tax_objects = []
  for taxid, data in taxon_info.items():
    if data['rank'] == 'assembly':
      name = assembly_names.get(taxid, taxid)
    else:
      name = ncbi_names.get(taxid, f'Taxon {taxid}')
    tax_objects.append(Taxonomy(
      taxid=taxid, rank=data['rank'], name=name, **data['lineage']
    ))

  batch_size = 500
  for i in range(0, len(tax_objects), batch_size):
    Taxonomy.objects.bulk_create(tax_objects[i:i+batch_size])
  print(f'  Created {len(tax_objects)} Taxonomy entries')


# === Step 2: Load tRNAs ===

def load_trnas():
  print('\n=== Step 2: Loading tRNAs ===')
  tRNAModel.objects.all().delete()
  total = 0

  for dname, files in DATA_DIRS.items():
    print(f'  Reading {dname} tRNAs...')
    batch = []

    with open(files['trnas'], 'r') as f:
      reader = csv.DictReader(f, delimiter='\t')
      for row in reader:
        kwargs = {}
        for col, value in row.items():
          field = tsv_col_to_field(col)
          if field == 'primary':
            value = (value == 'True')
          elif field in ('score', 'isoscore', 'isoscore_ac', 'GCcontent'):
            value = float(value)
          elif field in ('insertions', 'deletions', 'intron_length',
                         'dloop', 'acloop', 'tpcloop', 'varm'):
            value = int(value)
          elif value == '':
            value = None
          kwargs[field] = value

        batch.append(tRNAModel(**kwargs))

        if len(batch) >= 5000:
          tRNAModel.objects.bulk_create(batch)
          total += len(batch)
          batch = []
          print(f'    {total} tRNAs loaded...')

    if batch:
      tRNAModel.objects.bulk_create(batch)
      total += len(batch)

  print(f'  Created {total} tRNA entries')
  return total


# === Step 3: Compute Freq ===

def load_trna_dataframe():
  """Load all tRNA data into a dict-of-lists for efficient computation."""
  import pandas as pd
  single_fields = [pos_to_field(p) for p in SUMMARY_SINGLE_POSITIONS]
  paired_fields = [pos_to_field(p) for p in SUMMARY_PAIRED_POSITIONS]
  rank_fields = [RANK_TO_FIELD[r] for r in RANKS]
  columns = ['isotype'] + rank_fields + single_fields + paired_fields
  qs = tRNAModel.objects.all().values_list(*columns)
  df = pd.DataFrame(list(qs), columns=columns)
  print(f'  Loaded {len(df)} tRNAs into DataFrame')
  return df


def compute_freqs(df):
  print('\n=== Step 3: Computing Freq data ===')
  import pandas as pd

  Freq.objects.all().delete()
  taxonomies = list(Taxonomy.objects.all().values('taxid', 'rank'))
  print(f'  Computing for {len(taxonomies)} taxa x {len(ISOTYPES)+1} isotypes...')

  freq_objects = []
  total = 0

  for tax_idx, tax in enumerate(taxonomies):
    taxid = tax['taxid']
    rank = tax['rank']
    field = RANK_TO_FIELD.get(rank, rank)

    if field not in df.columns:
      continue
    tax_df = df[df[field] == taxid]
    if len(tax_df) == 0:
      continue

    for isotype in ISOTYPES + ['All']:
      iso_df = tax_df if isotype == 'All' else tax_df[tax_df['isotype'] == isotype]
      if len(iso_df) == 0:
        continue

      # Single positions
      for pos in SUMMARY_SINGLE_POSITIONS:
        fn = pos_to_field(pos)
        if fn not in iso_df.columns:
          continue
        counts = iso_df[fn].value_counts()
        freq_objects.append(Freq(
          taxid=taxid, isotype=isotype, position=pos, total=len(iso_df),
          A=int(counts.get('A', 0)), C=int(counts.get('C', 0)),
          G=int(counts.get('G', 0)), U=int(counts.get('U', 0)),
          Absent=int(counts.get('-', 0)),
        ))

      # Paired positions
      for pos in SUMMARY_PAIRED_POSITIONS:
        fn = pos_to_field(pos)
        if fn not in iso_df.columns:
          continue
        counts = iso_df[fn].value_counts()
        kwargs = {'taxid': taxid, 'isotype': isotype, 'position': pos,
                  'total': len(iso_df)}
        for pair_str, attr in PAIRED_FEATURE_MAP.items():
          kwargs[attr] = int(counts.get(pair_str, 0))
        freq_objects.append(Freq(**kwargs))

    if len(freq_objects) >= 10000:
      Freq.objects.bulk_create(freq_objects)
      total += len(freq_objects)
      freq_objects = []

    if (tax_idx + 1) % 200 == 0:
      print(f'    {tax_idx+1}/{len(taxonomies)} taxa processed, {total} freq entries...')

  if freq_objects:
    Freq.objects.bulk_create(freq_objects)
    total += len(freq_objects)

  print(f'  Created {total} Freq entries')


# === Step 4: Compute Consensus ===

def compute_consensus(df):
  print('\n=== Step 4: Computing Consensus data ===')
  import pandas as pd

  Consensus.objects.all().delete()
  taxonomies = list(Taxonomy.objects.all().values('taxid', 'rank'))
  print(f'  Computing consensus for {len(taxonomies)} taxa...')

  cons_objects = []
  total = 0

  for tax_idx, tax in enumerate(taxonomies):
    taxid = tax['taxid']
    rank = tax['rank']
    field = RANK_TO_FIELD.get(rank, rank)
    if field not in df.columns:
      continue
    tax_df = df[df[field] == taxid]
    if len(tax_df) == 0:
      continue

    for isotype in ISOTYPES + ['All']:
      iso_df = tax_df if isotype == 'All' else tax_df[tax_df['isotype'] == isotype]
      if len(iso_df) == 0:
        continue

      n = len(iso_df)
      cons_kwargs = {'taxid': taxid, 'isotype': isotype, 'datatype': 'Consensus'}
      near_kwargs = {'taxid': taxid, 'isotype': isotype, 'datatype': 'Near-consensus'}

      for pos in SUMMARY_SINGLE_POSITIONS:
        fn = pos_to_field(pos)
        field_name = fn  # model field name
        if fn not in iso_df.columns:
          cons_kwargs[field_name] = None
          near_kwargs[field_name] = None
          continue
        counts = dict(iso_df[fn].value_counts())
        cons_kwargs[field_name] = determine_single_consensus(counts, n, 0.5)
        near_kwargs[field_name] = determine_single_consensus(counts, n, 0.25)

      for pos in SUMMARY_PAIRED_POSITIONS:
        fn = pos_to_field(pos)
        field_name = fn
        if fn not in iso_df.columns:
          cons_kwargs[field_name] = None
          near_kwargs[field_name] = None
          continue
        counts = dict(iso_df[fn].value_counts())
        cons_kwargs[field_name] = determine_paired_consensus(counts, n, 0.5)
        near_kwargs[field_name] = determine_paired_consensus(counts, n, 0.25)

      cons_objects.append(Consensus(**cons_kwargs))
      cons_objects.append(Consensus(**near_kwargs))

    if len(cons_objects) >= 5000:
      Consensus.objects.bulk_create(cons_objects)
      total += len(cons_objects)
      cons_objects = []

    if (tax_idx + 1) % 200 == 0:
      print(f'    {tax_idx+1}/{len(taxonomies)} taxa processed, {total} consensus entries...')

  if cons_objects:
    Consensus.objects.bulk_create(cons_objects)
    total += len(cons_objects)

  print(f'  Created {total} Consensus entries')


# === Step 5: Load Coord ===

def load_coords():
  print('\n=== Step 5: Loading Coord data ===')

  # Cloverleaf coordinates: position -> (x, y, radius)
  # 95 positions laid out as a standard tRNA cloverleaf in 525x550 space
  r = 10
  COORD_DATA = {
    # Discriminator
    '73': (262, 30, r),
    # Acceptor stem (1-7 left, 72-66 right, vertical)
    '1': (235, 65, r), '72': (289, 65, r),
    '2': (235, 93, r), '71': (289, 93, r),
    '3': (235, 121, r), '70': (289, 121, r),
    '4': (235, 149, r), '69': (289, 149, r),
    '5': (235, 177, r), '68': (289, 177, r),
    '6': (235, 205, r), '67': (289, 205, r),
    '7': (235, 233, r), '66': (289, 233, r),
    # Connector 8-9
    '8': (212, 260, r), '9': (188, 283, r),
    # D-stem (10-13 left, 25-22 right)
    '10': (165, 305, r), '25': (115, 305, r),
    '11': (165, 333, r), '24': (115, 333, r),
    '12': (165, 361, r), '23': (115, 361, r),
    '13': (165, 389, r), '22': (115, 389, r),
    # D-loop (14-21, 17a, 20a, 20b)
    '14': (148, 415, r), '15': (125, 430, r), '16': (100, 438, r),
    '17': (75, 435, r), '17a': (55, 422, r), '18': (42, 402, r),
    '19': (42, 378, r), '20': (55, 358, r), '20a': (75, 348, r),
    '20b': (95, 345, r), '21': (102, 402, r),
    # Connector 26
    '26': (192, 375, r),
    # Anticodon stem (27-31 left, 43-39 right)
    '27': (218, 400, r), '43': (268, 400, r),
    '28': (218, 428, r), '42': (268, 428, r),
    '29': (218, 456, r), '41': (268, 456, r),
    '30': (218, 484, r), '40': (268, 484, r),
    '31': (218, 512, r), '39': (268, 512, r),
    # Anticodon loop (32-38)
    '32': (208, 534, r), '33': (215, 548, r), '34': (228, 558, r),
    '35': (243, 562, r), '36': (258, 558, r), '37': (271, 548, r),
    '38': (278, 534, r),
    # Connector 44-48
    '44': (288, 375, r), '45': (308, 352, r),
    '46': (322, 332, r), '47': (335, 310, r), '48': (342, 288, r),
    # Variable arm (V1-V5)
    'V1': (302, 398, r), 'V2': (318, 412, r), 'V3': (336, 420, r),
    'V4': (354, 422, r), 'V5': (370, 416, r),
    # Variable arm stem (V11-V17 left, V21-V27 right)
    'V11': (372, 432, r), 'V21': (398, 432, r),
    'V12': (372, 452, r), 'V22': (398, 452, r),
    'V13': (372, 472, r), 'V23': (398, 472, r),
    'V14': (372, 492, r), 'V24': (398, 492, r),
    'V15': (372, 512, r), 'V25': (398, 512, r),
    'V16': (372, 532, r), 'V26': (398, 532, r),
    'V17': (372, 552, r), 'V27': (398, 552, r),
    # T-stem (49-53 left, 65-61 right)
    '49': (358, 265, r), '65': (408, 265, r),
    '50': (358, 237, r), '64': (408, 237, r),
    '51': (358, 209, r), '63': (408, 209, r),
    '52': (358, 181, r), '62': (408, 181, r),
    '53': (358, 153, r), '61': (408, 153, r),
    # T-loop (54-60)
    '54': (348, 132, r), '55': (352, 112, r), '56': (365, 97, r),
    '57': (383, 90, r), '58': (401, 97, r), '59': (414, 112, r),
    '60': (418, 132, r),
  }

  assert len(COORD_DATA) == 95, f'Expected 95 coords, got {len(COORD_DATA)}'

  Coord.objects.all().delete()
  coord_objects = [
    Coord(position=pos, x=x, y=y, radius=radius)
    for pos, (x, y, radius) in COORD_DATA.items()
  ]
  Coord.objects.bulk_create(coord_objects)
  print(f'  Created {len(coord_objects)} Coord entries')


# === Main ===

if __name__ == '__main__':
  start = time.time()
  print('tRNAviz Data Loader')
  print('=' * 40)

  load_taxonomy()
  load_trnas()

  print('\n  Loading tRNA DataFrame for Freq/Consensus computation...')
  df = load_trna_dataframe()

  compute_freqs(df)
  compute_consensus(df)
  load_coords()

  elapsed = time.time() - start
  print(f'\n{"=" * 40}')
  print(f'Done! Total time: {elapsed:.0f}s')
  print(f'\nDatabase summary:')
  print(f'  Taxonomy: {Taxonomy.objects.count()}')
  print(f'  tRNA:     {tRNAModel.objects.count()}')
  print(f'  Freq:     {Freq.objects.count()}')
  print(f'  Consensus:{Consensus.objects.count()}')
  print(f'  Coord:    {Coord.objects.count()}')
