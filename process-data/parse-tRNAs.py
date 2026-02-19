#!/usr/bin/env python
import sys, os
message = lambda s: print(s, file = sys.stderr, end = '', flush = True)
message('Loading packages...')
import numpy
import pandas as pd
import argparse
import subprocess
import datetime
import re
from collections import defaultdict
from Bio import SeqIO, SeqRecord, Seq
from tRNA_position import annotate_positions, get_position_base_from_seq
message('done\n')

def main():
  message('== Parsing tRNAs for domain {} ==\n'.format(domain))
  message('Loading species data from {}...'.format(genome_table_path))
  genomes_df = read_genomes_table(genome_table_path)
  message('done\n')

  message('Processing tRNAscan-SE output\n')
  seqs, trna_metadata = process_tscan_output(genomes_df)
  message('Done\n')
  
  message('Writing seqs in FASTA format to {}...'.format(tRNA_fasta))
  fasta_handle = open(tRNA_fasta, 'w')
  SeqIO.write(seqs, fasta_handle, 'fasta')
  fasta_handle.close()
  message('done\n')

  message('Aligning sequences to numbering model {} and saving to {}...'.format(numbering_model, alignment_file))
  subprocess.check_call('cmalign -g --notrunc {} {} > {}'.format(numbering_model, tRNA_fasta, alignment_file), shell=True)
  message('done\n')

  message('Parsing alignment model into Positions...')
  positions = parse_alignment_cons()
  message('done\n')

  message('Parsing individual tRNAs into data frame...')
  trnas = parse_alignment_into_trna_df(positions)
  message('done\n')

  message('Combine tRNA metadata, taxonomy, and features...')
  trnas = trnas.join(trna_metadata)
  trnas = trnas.join(genomes_df.drop(['iso_file', 'ss_file', 'out_file', 'tRNA_file', 'taxid', 'name'], axis = 1).set_index('dbname'), on = 'dbname')
  message('done\n')

  message('Annotating tRNAs...\n')
  trnas = annotate_trnas(trnas)
  message('Done\n')

  message('Exporting results to {}...'.format(output_file))
  trnas = trnas[sorted(list(trnas.columns), key = get_position_order)]
  if not output_insertion_columns:
    insertion_cols = list(filter(lambda x: bool(re.search('^V?\d+a?b?i', x)), trnas.columns))
    trnas.drop(columns = insertion_cols, inplace = True)

  trnas.to_csv(path_or_buf = output_file, sep = '\t', index_label = 'seqname')
  message('done\n')


def read_genomes_table(path):
  '''Read genomes table, then add and validate paths to tRNAscan-SE output to genomes data frame'''
  genomes_df = pd.read_table(path, index_col = False, dtype = {
    'dbname': str,
    'taxid': str,
    'name': str,
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
    'assembly': str
  })

  genomes_df['iso_file'] = genomes_df.dbname.apply(lambda dbname: 'data/iso/{}-tRNAs.iso'.format(dbname))
  genomes_df['ss_file'] = genomes_df.dbname.apply(lambda dbname: 'data/ss/{}-tRNAs.ss'.format(dbname))
  genomes_df['tRNA_file'] = genomes_df.dbname.apply(lambda dbname: 'data/tRNAs/{}-tRNAs.fa'.format(dbname))
  genomes_df['out_file'] = genomes_df.dbname.apply(lambda dbname: 'data/out/{}-tRNAs.out'.format(dbname))

  # Validate files
  for row in genomes_df.itertuples():
    for file_type in ['iso_file', 'ss_file', 'out_file']:
      if not os.path.exists(getattr(row, file_type)):
        if domain == 'euk':
          detailed_out_file = 'data/out/{}-tRNAs-detailed.out'.format(row.dbname)
          if os.path.exists(detailed_out_file):
            genomes_df.loc[genomes_df['taxid'] == row.taxid, 'out_file'] = detailed_out_file
            continue
        raise Exception('{} does not exist for {}'.format(file_type, getattr(row, file_type)))

  return genomes_df



def process_tscan_output(genomes_df):
  '''Process and filter tRNAs from .out, .ss, and .iso output'''
  seqs = [] # final sequence list
  trna_metadata = [] # to be converted into a data frame

  for row in genomes_df.itertuples():
    message('\tProcessing tRNAs from {} ({})...'.format(row.name, row.taxid))

    # Process .out file. We want a list of approved tRNAs and their intron lengths.
    approved_tRNAs = []
    intron_lengths = []
    tscanout_dtypes = {'seqname': str, 'start': int, 'end': int, 'isotype': str, 'ac': str, 'intron_start': str, 'intron_end': str, 
      'score': float, 'hmm_score': float, 'best_model': str, 'best_score': float}
    try:
      tscanout_cols = ['seqname', 'trna_number', 'start', 'end', 'isotype', 'ac', 'intron_start', 'intron_end', 'score', 'hmm_score', 'sec_score', 'inf', 'best_model', 'best_score', 'type', 'note']
      tscanout = pd.read_table(row.out_file, sep = "\t", skiprows = 3, na_filter = False, header = None, names = tscanout_cols, dtype = tscanout_dtypes)
    except ValueError:
      try:
        tscanout_cols.remove('type')
        tscanout = pd.read_table(row.out_file, sep = "\t", skiprows = 3, na_filter = False, header = None, names = tscanout_cols, dtype = tscanout_dtypes)
      except ValueError:
        try:
          tscanout_cols.remove('inf')
          tscanout = pd.read_table(row.out_file, sep = "\t", skiprows = 3, na_filter = False, header = None, names = tscanout_cols, dtype = tscanout_dtypes)
        except ValueError:
          tscanout = pd.read_table(row.out_file, sep = "\s+", skiprows = 3, na_filter = False, header = None, names = tscanout_cols, dtype = tscanout_dtypes)
    for metadata in tscanout.itertuples():
      # Filter out tRNAs
      if 'pseudo' in metadata.note or 'trunc' in metadata.note or metadata.score < 25:
        continue
      if domain == 'euk':
        if row.phylum == '7711': # Chordata
          valid_notes = ['high confidence set']
        else:
          valid_notes = ["", "high confidence set", "secondary filtered", "tertiary filtered", "Quality set", 
            "unexpected anticodon", "Unexpected anticodon;First-pass quality filtered", "Isotype mismatch;First-pass quality filtered", 
            "First-pass quality filtered", "Second-pass quality filtered", "Isotype mismatch;Isotype mismatch;First-pass quality filtered"]
        if metadata.note not in valid_notes: continue
        if row.kingdom != '4751' and metadata.score < 50: continue

      # Set isotype
      isotype = metadata.isotype.strip()
      if 'exon' in metadata.isotype:
        isotype, exon = isotype.split('-')
        # don't double count multiple exon tRNAs
        if exon != 'exon1':
          continue
      if isotype == 'Met':
        if metadata.best_model.strip() in ['iMet', 'fMet', 'Ile2']: isotype = metadata.best_model.strip()

      # Save tRNAs
      # Track canonical intron length separately
      if 'NCI' in metadata.note:
        # Handle multiple introns. Need to figure out which one is the canonical intron, then calculate length. The intron closest to index 39 of the tRNA is listed as the canonical intron.
        # Canonical introns are located after 37 (index 38), and most tRNAs contain at least 1 extra base in the D-loop -> index 39
        if 'CI' in metadata.note.split(','):
          start, end = metadata.start, metadata.end
          intron_starts = [int(s) for s in metadata.intron_start.split(',')]
          intron_ends = [int(s) for s in metadata.intron_end.split(',')]
          pos_starts = []
          if start < end:
            pos_starts.append(intron_starts[0] - start)
            pos_starts.append(intron_starts[1] - (intron_ends[0] - intron_starts[0]) - start)
            if len(intron_starts) > 2:
              pos_starts.append(intron_starts[1] - (intron_ends[0] - intron_starts[0]) - (intron_ends[1] - intron_starts[1]) - start)
            canonical_intron_index = numpy.argmin([abs(s - 39) for s in pos_starts])
            intron_length = intron_ends[canonical_intron_index] - intron_starts[canonical_intron_index]
          elif end < start:
            pos_starts.append(start - intron_starts[0])
            pos_starts.append(start - (intron_starts[0] - intron_ends[0]) - intron_starts[1])
            if len(intron_starts) > 2:
              pos_starts.append(start - (intron_starts[0] - intron_ends[0]) - (intron_starts[1] - intron_ends[1]) - intron_starts[2])
            canonical_intron_index = numpy.argmin([abs(s - 39) for s in pos_starts])
            intron_length = intron_starts[canonical_intron_index] - intron_ends[canonical_intron_index] + 1
      else:
        intron_length = abs(int(metadata.intron_start) - int(metadata.intron_end))
      if intron_length > 0: intron_length = intron_length + 1
      intron_lengths.append(intron_length)
      seqname = '{}.trna{}-{}{}'.format(metadata.seqname.strip(), metadata.trna_number, isotype, metadata.ac.strip())
      approved_tRNAs.append(seqname)

    # Parse isotype-specific scores
    iso_scores = get_iso_scores(row.iso_file)

    # Generate new tRNA fasta file by removing introns
    subprocess.call('sstofa3 {} "" 1 0 > {}'.format(row.ss_file, row.tRNA_file), shell = True)

    # Go through tRNAs, filter based on approved_tRNAs
    # Also regenerate headers with more metadata - we will need the metadata later post-alignment
    for seq in SeqIO.parse(row.tRNA_file, 'fasta'):
      if seq.id not in approved_tRNAs or "pseudogene" in seq.description:
        continue
      seqname, _, isotype, anticodon, _, _, _, score = seq.description.strip().split()
      trnascanid = re.findall('.+\.trna\d+', seq.id)[0]
      seqname = '{}_{}'.format(row.dbname, seqname)
      score = float(score)
      anticodon = anticodon[1:-1]
      best_model = iso_scores.loc[trnascanid].best_model
      if best_model == 'SeC' or 'mito' in best_model or 'mt' in seqname: continue
      isoscore = iso_scores.loc[trnascanid].score
      isoscore_ac = iso_scores.loc[trnascanid].isoscore_ac
      intron_length = intron_lengths[approved_tRNAs.index(seq.id)]

      trna = {
        'dbname': row.dbname,
        'seqname': seqname,
        'isotype': isotype,
        'anticodon': anticodon,
        'score': score,
        'best_model': best_model,
        'isoscore': isoscore,
        'isoscore_ac': isoscore_ac,
        'intron_length': intron_length
      }

      seq.id = seqname
      seq.description = ''
      seqs.append(seq)
      trna_metadata.append(trna)

    message('done\n')

  trna_metadata = pd.DataFrame(trna_metadata).set_index('seqname')
  return seqs, trna_metadata

def get_iso_scores(iso_file):
  iso_scores = pd.read_table(iso_file, header = 0)
  iso_scores['Undet'] = 0
  iso_scores['Sup'] = 0
  iso_scores['best_model'] = iso_scores.iloc[:, 2:].idxmax(axis = 1)
  iso_scores['score'] = iso_scores.max(axis = 1, numeric_only = True)
  iso_scores['isoscore_ac'] = iso_scores.lookup(iso_scores.index, iso_scores.iloc[:, 1])
  iso_scores.index = iso_scores.tRNAscanID.values
  iso_scores = iso_scores[['best_model', 'score', 'isoscore_ac']]
  return iso_scores


def parse_alignment_cons():
  alignment_fhandle = open(alignment_file)
  ss = ''
  for line in alignment_fhandle:
    if line[0:12] == '#=GC SS_cons':
      ss += line.strip().split()[-1]
  alignment_fhandle.close()

  # parse secondary structure into Positions
  return annotate_positions(ss)


def parse_alignment_into_trna_df(positions):
  '''Parse alignment; for each tRNA, get base at each Position, then convert list of tRNAs into data frame'''

  trnas = []
  seqs = defaultdict(str)
  seqnames = []

  # Read in seqs that may be split into multiple lines
  alignment_fhandle = open(alignment_file)
  for line in alignment_fhandle:
    if line[0] in ["#", '\n', '/']:
      continue
    seqname, seq = line.strip().split()
    if seqname not in seqnames: seqnames.append(seqname)
    seqs[seqname] += seq
  alignment_fhandle.close() 
  
  for seqname in seqnames:
    trnas.append({
      'seqname': seqname,
      **{sprinzl: base for sprinzl, base in get_position_base_from_seq(positions, seqs[seqname])}
    })

  trnas = pd.DataFrame(trnas).set_index('seqname')
  trnas.fillna('.', inplace=True)
  return trnas


def annotate_trnas(trnas):
  message('\tAdjusting isotype designations for Met, iMet and Ile2...')
  imet_indices = trnas[(trnas.isotype == "Met") & (trnas.best_model == "iMet")].index
  trnas.loc[imet_indices, 'isotype'] = 'iMet'
  fmet_indices = trnas[(trnas.isotype == "Met") & (trnas.best_model == "fMet")].index
  trnas.loc[fmet_indices, 'isotype'] = 'fMet'
  ile2_indices = trnas[(trnas.isotype == "Met") & (trnas.best_model == "Ile2")].index
  trnas.loc[ile2_indices, 'isotype'] = 'Ile2'
  message('done\n')

  message('\tCalculating stem GC content...')
  gc_cols = list(filter(lambda x: re.search('\d', x) and ':' not in x, trnas.columns))
  trnas['GCcontent'] = trnas[gc_cols].apply(lambda x: sum((x == 'G') | (x == 'C')) / sum((x != '-') & (x != '.')), axis = 1)
  message('done\n')

  message('\tSplitting paired to single base columns...')
  paired_cols = list(filter(lambda x: ':' in x, trnas.columns))
  for col in paired_cols:
    pos1, pos2 = col.split(':')
    base1 = [bases.split(':')[0] for bases in trnas[col]]
    base2 = [bases.split(':')[1] for bases in trnas[col]]
    trnas[pos1], trnas[pos2] = base1, base2
  message('done\n')

  message('\tAdding tertiary interaction columns...')
  for tertiary_interaction in ['8:14', '9:23', '10:45', '22:46', '15:48', '18:55', '19:56', '26:44', '54:58']:
    bases = tertiary_interaction.split(':')
    trnas[tertiary_interaction] = trnas.loc[:, bases].apply(lambda row: ':'.join(row), axis = 1)
  message('done\n')

  message('\tAdding indel columns...')
  # Insertions (minus misaligned introns at 37/38)
  intron_cols = list(filter(lambda x: x[0:3] == '37i', trnas.columns))
  insertion_cols = list(filter(lambda x: bool(re.search('^\d+i', x)) & (x not in intron_cols), trnas.columns))
  trnas['insertions'] = trnas[insertion_cols].apply(lambda x: sum(x != '.'), axis=1)
  base_cols = list(filter(lambda x: bool(re.match('^\d+$', x)) & (x not in ['74', '75', '76', '17', '17a', '20a', '20b']), trnas.columns))
  trnas['deletions'] = trnas[base_cols].apply(lambda x: ''.join(x).count('-'), axis=1)
  message('done\n')

  message('\tCalculating loop lengths\n')
  message('\t\tCalculating D-loop lengths...')
  dloop_cols = list(filter(lambda col: ':' not in col, bounds_to_cols(trnas.columns, 14, 21)))
  trnas['dloop'] = trnas[dloop_cols].apply(lambda x: len(x[(x != '.') & (x != '-')]), axis = 1)
  # Leu, Ser have a 3 bp D stem
  dloop_II_cols = list(filter(lambda col: ':' not in col, bounds_to_cols(trnas.columns, 13, 22)))
  if domain == 'bact':
    trnas.loc[(trnas.isotype == 'Leu') | (trnas.isotype == 'Ser') | (trnas.isotype == 'Tyr'), 'dloop'] = trnas[dloop_II_cols].apply(lambda x: len(x[(x != '.') & (x != '-')]), axis = 1)
  else:
    trnas.loc[(trnas.isotype == 'Leu') | (trnas.isotype == 'Ser'), 'dloop'] = trnas[dloop_II_cols].apply(lambda x: len(x[(x != '.') & (x != '-')]), axis = 1)
  message('done\n')
  message('\t\tCalculating anticodon loop lengths...')
  acloop_cols = list(filter(lambda x: not re.match('37i.+', x), bounds_to_cols(trnas.columns, 32, 38)))
  trnas['acloop'] = trnas[acloop_cols].apply(lambda x: len(x[(x != '.') & (x != '-')]), axis = 1)
  message('done\n')
  message(u'\t\tCalculating TψC loop lengths...')
  tpcloop_cols = bounds_to_cols(trnas.columns, 54, 60)
  trnas['tpcloop'] = trnas[tpcloop_cols].apply(lambda x: len(x[(x != '.') & (x != '-')]), axis = 1)
  message('done\n')
  message(u'\t\tCalculating variable arm lengths...')
  varm_cols = list(filter(lambda x: ('V' in x) & (':' not in x) | (x in bounds_to_cols(trnas.columns, 45, 48)), trnas.columns))
  trnas['varm'] = trnas[varm_cols].apply(lambda x: len(x[(x != '.') & (x != '-')]), axis = 1)
  message('done\n')

  message('\tMarking duplicates...')
  trnas['primary'] = trnas.groupby(['species', 'isotype'], group_keys = False).apply(lambda subset: -subset.score.duplicated())
  message('done\n')

  return(trnas)

def bounds_to_cols(cols, start, end):
  '''Helper function for identifying variable number of positions within tRNA loops'''
  selected_cols = []
  for col in cols:
    matches = re.findall('\d+', col)
    if len(matches) < 1: continue
    index = int(matches[0])
    if (index >= start and index <= end or col[0:3] == '{}i'.format(start - 1)) and col[0] != 'V':
      selected_cols.append(col)
  return selected_cols


def get_position_order(position):
  '''Helper function for returning a value for sorting position-based columns, especially with variable insertions'''
  metadata_cols = ['isotype', 'anticodon', 'score', 'primary', 'best_model', 'isoscore', 'isoscore_ac', 'dbname', 'domain', 'kingdom', 'subkingdom', 'phylum', 'subphylum', 'class', 'subclass', 'order', 'family', 'genus', 'species', 'assembly', 'GCcontent', 'insertions', 'deletions', 'D-loop', 'AC-loop', 'TPC-loop', 'V-arm', 'intron_length']
  if position in metadata_cols:
    return metadata_cols.index(position) - 50
  if position == "20a": return 20.1
  if position == "20b": return 20.2
  digits = re.findall('\d+', position)
  if len(digits) == 0: return -1
  insert = 0
  if 'i' in position and len(digits) == 2: insert = float(digits[1]) / 1000
  if position[0] == 'V':
    if ':' in position: return int(digits[0]) + 45 - 10 + insert # V11~V17
    else: return int(digits[0]) + 45 + 7 + insert # V1~V5
  if int(digits[0]) >= 46: return int(digits[0]) + 100 + insert # just add an arbitrarily large number to skip v-arm
  return int(digits[0]) + insert


def parse_args():
  parser = argparse.ArgumentParser(description = "Generate table of tRNA features using tRNAscan-SE output")
  parser.add_argument('-d', '--domain', required = True, choices = ['bact', 'euk', 'arch'], help = 'Select domain (euk, bact, or arch)')
  parser.add_argument('-g', '--genome_table_path', default = 'genomes.tsv', help = '')
  parser.add_argument('-n', '--numbering_model', required = True, help = 'Covariance model optimized for tRNA numbering')
  parser.add_argument('-o', '--output_file', default = 'tRNAs-{}.tsv'.format(timestamp), help = '')
  parser.add_argument('-a', '--alignment_file', default = 'tRNAs-{}.sto'.format(timestamp), help = '')
  parser.add_argument('-f', '--tRNA_fasta', default = 'tRNAs-{}.fa'.format(timestamp), help = '')
  parser.add_argument('-c', '--clean', default = False, action = 'store_true', help = 'Attempt to automatically clean up intermediate files')
  parser.add_argument('-i', '--output_insertion_columns', default = False, action = 'store_true', help = 'Include columns for introns and insertions')
  return parser.parse_args()


if __name__ == '__main__':
  timestamp = '{:%m%d%y-%H%M%S}'.format(datetime.datetime.now())
  args = parse_args()
  domain = args.domain
  genome_table_path = args.genome_table_path
  tRNA_fasta = args.tRNA_fasta
  alignment_file = args.alignment_file
  numbering_model = args.numbering_model
  output_file = args.output_file
  output_insertion_columns = args.output_insertion_columns
  main()
  if args.clean:
    os.remove(alignment_file)
    os.remove(tRNA_fasta)
