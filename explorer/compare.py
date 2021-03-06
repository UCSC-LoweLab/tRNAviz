from django.http import JsonResponse
from django.conf import settings
from django.db.models import Q
from django.core.exceptions import ValidationError

import os
import re
import json
import subprocess
from collections import defaultdict
from tempfile import NamedTemporaryFile
from Bio import SeqIO
import pandas as pd
from django_pandas.io import read_frame

from . import models
from . import choices

INFERNAL_BIN = '/www/bin/'

SINGLE_FEATURES = {'A': 'A', 'C': 'C', 'G': 'G', 'U': 'U', 'absent': '-'}
PAIRED_FEATURES = {
  'AU': 'A:U', 'UA': 'U:A', 'GC': 'G:C', 'CG': 'C:G', 'GU': 'G:U', 'UG': 'U:G', 
  'AA': 'A:A', 'AC': 'A:C', 'AG': 'A:G', 'CA': 'C:A', 'CC': 'C:C', 'CU': 'C:U', 'GA': 'G:A', 'GG': 'G:G', 'UC': 'U:C', 'UU': 'U:U',
  'AM': 'A:-', 'CM': 'C:-', 'GM': 'G:-', 'UM': 'U:-', 'MA': '-:A', 'MC': '-:C', 'MG': '-:G', 'MU': '-:U', 'MM': '-:-'
}
IUPAC_CODES = {}
IUPAC_CODES.update(SINGLE_FEATURES)
IUPAC_CODES.update(PAIRED_FEATURES)
IUPAC_CODES.update({'Absent': '-', 'Purine': 'R', 'Pyrimidine': 'Y', 'Amino': 'M', 'Keto': 'K', 'Weak': 'W', 'Strong': 'S', 
  'B': 'B', 'D': 'D', 'H': 'H', 'V': 'V', 'N': 'N', 
  'PurinePyrimidine': 'R:Y', 'PyrimidinePurine': 'Y:R', 'WobblePair': 'K:K', 'StrongPair': 'S:S', 'WeakPair': 'W:W', 'AminoKeto': 'M:K', 'KetoAmino': 'K:M', 
  'Paired': 'N:N', 'Bulge': '', 'Mismatched': 'N|N', 'High mismatch rate': 'N|N', 'NN': '', '': ''})
HUMAN_LABELS = {
  'Amino': 'A / C', 'Keto': 'G / U', 'Weak': 'A / U', 'Strong': 'G / C', 
  'B': 'C / G / U', 'H': 'A / C / U', 'D': 'A / G / U', 'V': 'A / C / G', 'N': 'N',
  'PurinePyrimidine': 'Purine:Pyrimidine', 'PyrimidinePurine': 'Pyrimidine:Purine',
  'WobblePair': 'G:U / U:G', 'StrongPair': 'G:C / C:G', 'WeakPair': 'A:U / U:A', 'AminoKeto': 'A:U / C:G', 'KetoAmino': 'G:C / U:A', 
  'Paired': 'Paired', 'Bulge': '-:N / N:-', 'Mismatched': 'Mismatched', 'NN': 'N:N'
}
HUMAN_LABELS.update(SINGLE_FEATURES)
HUMAN_LABELS.update(PAIRED_FEATURES)

BITCHART_POSITIONS = ['8', '9', '14', '15', '16', '17', '17a', '18', '19', '20', '20a', '20b', '21', '26', 
  '32', '33', '34', '35', '36', '37', '38', '44', '45', '46', '47', '48', '54', '55', '56', '57', '58', '59', '60', '73',
  '1:72', '2:71', '3:70', '4:69', '5:68', '6:67', '7:66', '10:25', '11:24', '12:23', '13:22', 
  '27:43', '28:42', '29:41', '30:40', '31:39', '49:65', '50:64', '51:63', '52:62', '53:61']

NUMBERING_MODELS = {'Universal': '{}/all-num.cm'.format(settings.ENGINE_DIR),
  'Eukaryota': '{}/euk-num.cm'.format(settings.ENGINE_DIR),
  'Bacteria': '{}/bact-num.cm'.format(settings.ENGINE_DIR),
  'Archaea': '{}/arch-num.cm'.format(settings.ENGINE_DIR)}

def bitchart(request, formset_json):
  try:
    # get formset
    formset_data = json.loads(open(settings.MEDIA_ROOT + formset_json).read())
    if (formset_json.find('default') == -1):
      os.remove(settings.MEDIA_ROOT + formset_json)
    seqs = read_all_trnas()
    trna_fasta_files = write_trnas_to_files(formset_data, seqs)
    ref_model_fh = build_reference_model(formset_data, trna_fasta_files)
    ref_bits = calculate_normalizing_scores(ref_model_fh)

    # Align tRNAs to reference model and collect bit scores
    bits = pd.DataFrame()
    for i, trna_fasta_fh in enumerate(trna_fasta_files[1:]):
      if formset_data[i + 2]['use_fasta'] == "True":
        num_model = NUMBERING_MODELS[formset_data[i + 2]['domain']]
      else:
        clade_tax = models.Taxonomy.objects.filter(taxid = formset_data[i + 2]['clade'])[0]
        num_model = NUMBERING_MODELS[models.Taxonomy.objects.filter(taxid = clade_tax.domain).get().name]
      current_bits = align_trnas_collect_bit_scores(trna_fasta_fh.name, num_model, ref_model_fh.name)
      current_bits['group_name'] = formset_data[i + 2]['name']
      current_bits['group'] = 'group-{}'.format(i)
      bits = bits.append(current_bits)

    # Normalize bits against reference bits
    bits['score'] = round(bits.apply(lambda x: x['score'] - ref_bits[ref_bits.position == x['position']]['score'].values[0], axis = 1), 2)

    # Append consensus and modal feature bits
    ref_taxid = formset_data[0]['clade']
    ref_isotype = formset_data[0]['isotype']
    ref_cons = get_cons_bits(ref_taxid, ref_isotype)
    ref_freqs = get_modal_freqs(ref_taxid, ref_isotype)
    bits = pd.concat([bits, ref_cons, ref_freqs], sort = True).reset_index(drop = True)
    
    # Format data for visualization
    plot_data = format_bits_for_viz(bits)
    return JsonResponse(plot_data, safe = False)
  
  except Exception as e:
    print(e)
    return JsonResponse({'server_error': 'Unknown error'})

def read_all_trnas():
  seqs = []
  seq_file_handle = open(settings.ENGINE_DIR + 'tRNAs.fa')
  for seq in SeqIO.parse(seq_file_handle, 'fasta'):
    seqs.append(seq)
  seq_file_handle.close()
  return seqs

def write_trnas_to_files(formset_data, seqs):
  # write tRNA sets to files
  trna_fasta_files = []
  for i, form_data in enumerate(formset_data):
    # Skip dummy form row
    if i == 1: continue 
    
    # Prepare tRNAs for writing to file
    trna_fasta_fh = NamedTemporaryFile('w', buffering = 1)
    trna_seqs = []

    # For selects, query db
    if 'use_fasta' not in form_data or form_data['use_fasta'] != "True":
      trna_qs = query_trnas(form_data)
      seqnames = [d['seqname'] for d in trna_qs]
      for seq in seqs:
        if seq.description in seqnames: trna_seqs.append(seq)
      SeqIO.write(trna_seqs, trna_fasta_fh, 'fasta')
    # otherwise write input directly into file
    else:
      trna_fasta_fh.write(form_data['fasta'])
    
    trna_fasta_fh.flush()
    trna_fasta_files.append(trna_fasta_fh)
  return trna_fasta_files

def query_trnas(form_data):
  clade_tax = models.Taxonomy.objects.filter(taxid = form_data['clade'])[0]
  rank = clade_tax.rank if clade_tax.rank != 'class' else 'taxclass'
  trna_qs = models.tRNA.objects.filter(Q(**{rank: clade_tax.taxid})).values('seqname')
  if form_data['isotype'] != 'All':
    trna_qs = trna_qs.filter(isotype = form_data['isotype'])
  return trna_qs

def build_reference_model(formset_data, trna_fasta_files):
  # Build reference CM model
  ref_fasta = trna_fasta_files[0].name
  ref_align_fh = NamedTemporaryFile()
  clade_tax = models.Taxonomy.objects.filter(taxid = formset_data[0]['clade'])[0]
  num_model = NUMBERING_MODELS[models.Taxonomy.objects.filter(taxid = clade_tax.domain).get().name]
  cmd_cmalign = INFERNAL_BIN + 'cmalign -g --notrunc --matchonly -o {} {} {} > /dev/null'.format(ref_align_fh.name, num_model, ref_fasta)
  res = subprocess.run(cmd_cmalign, shell = True)
  ref_model_fh = NamedTemporaryFile()
  cmd_cmbuild = INFERNAL_BIN + 'cmbuild --hand --enone -F {} {} > /dev/null'.format(ref_model_fh.name, ref_align_fh.name)
  res = subprocess.run(cmd_cmbuild, shell = True)
  return ref_model_fh

def calculate_normalizing_scores(ref_model_fh):
  # Get normalizing bit scores. To do this, we generate a consensus sequence and align it to the model.
  # Generate consensus sequence. First, build a consensus model with gaps.
  cons_model_fh = NamedTemporaryFile()
  cons_align_fh = NamedTemporaryFile()
  cons_fasta_fh = NamedTemporaryFile()
  cons_parsetree_fh = NamedTemporaryFile('r+')
  cmd_cmemit = INFERNAL_BIN + 'cmemit --exp 5 -N 1000 -a {} > {}'.format(ref_model_fh.name, cons_align_fh.name)
  res = subprocess.run(cmd_cmemit, shell = True)
  cmd_cmbuild = INFERNAL_BIN + 'cmbuild --enone -F {} {} > /dev/null'.format(cons_model_fh.name, cons_align_fh.name)
  res = subprocess.run(cmd_cmbuild, shell = True)

  # Emit a consensus sequence and format
  cmd_cmemit = INFERNAL_BIN + 'cmemit -c {}'.format(cons_model_fh.name)
  res = subprocess.run(cmd_cmemit, stdout = subprocess.PIPE, shell = True)
  cons_fasta_fh.write(res.stdout.upper())
  cons_fasta_fh.flush()

  # Align to reference model, and get normalizing bits
  cmd_cmalign = INFERNAL_BIN + 'cmalign -g --notrunc --matchonly --tfile {} {} {} > /dev/null'.format(cons_parsetree_fh.name, ref_model_fh.name, cons_fasta_fh.name)
  res = subprocess.run(cmd_cmalign, shell = True)
  ref_bits = pd.DataFrame(parse_parsetree(cons_parsetree_fh))
  ref_bits.group_name = 'Reference consensus'
  ref_bits.group = 'ref-cons'
  return ref_bits


def align_trnas_collect_bit_scores(trna_fasta, num_model, ref_model):
  num_model_align_fh = NamedTemporaryFile('r+')
  processed_fasta_fh = NamedTemporaryFile('r+', buffering = 1)
  parsetree_fh = NamedTemporaryFile('r+', buffering = 1)

  # Remove introns from all tRNAs (except reference). First, align to numbering model to purge insertions
  cmd_cmalign = INFERNAL_BIN + 'cmalign -g --notrunc --matchonly -o {} {} {} > /dev/null'.format(num_model_align_fh.name, num_model, trna_fasta)
  res = subprocess.run(cmd_cmalign, shell = True)

  # remove introns using alignment and rewrite tRNAs to new file
  for line in num_model_align_fh:
    if line[0] in ['#', '/', '\n']: continue
    seqname, seq = line.strip().split()
    seq = seq.replace('-', '')
    processed_fasta_fh.write('>{}\n{}\n'.format(seqname, seq))

  # realign to reference model and parse parsetree output
  cmd_cmalign = INFERNAL_BIN + 'cmalign -g --notrunc --matchonly --tfile {} -o /dev/null {} {} > /dev/null'.format(parsetree_fh.name, ref_model, processed_fasta_fh.name)
  res = subprocess.run(cmd_cmalign, shell = True)
  bits = pd.DataFrame(parse_parsetree(parsetree_fh))
  
  # For selections with mutliple tRNAs, summarize by average score and modal feature
  num_trnas = len(bits.seqname.unique())
  modal_features = bits.groupby('position').apply(lambda x: x['feature'].mode()[0]).reset_index().rename(columns = {0: 'feature'})
  bits = bits.set_index(['seqname', 'feature', 'position']).groupby('position').mean()
  bits = bits.join(modal_features.set_index('position')).reset_index()
  bits = bits[['feature', 'position', 'score']]
  bits['total'] = num_trnas
  return bits

def get_cons_bits(ref_taxid, ref_isotype):
  ref_cons_qs = models.Consensus.objects.filter(taxid = ref_taxid, isotype = ref_isotype, datatype = 'Consensus').values()
  ref_cons = read_frame(ref_cons_qs).drop(['id', 'taxid', 'isotype'], axis = 1).stack().unstack(0).reset_index()
  ref_cons.columns = ['position', 'feature']
  ref_cons.position = ref_cons.position.apply(lambda x: x[1:].replace('_', ':'))
  ref_cons['score'] = 0
  ref_cons['total'] = ''
  ref_cons['group_name'] = 'Reference consensus'
  ref_cons['group'] = 'ref-cons'
  return ref_cons

def get_modal_freqs(ref_taxid, ref_isotype):
  freqs_qs = models.Freq.objects.filter(taxid = ref_taxid, isotype = ref_isotype).values()
  ref_freqs = read_frame(freqs_qs).drop(['id', 'taxid', 'isotype'], axis = 1)
  ref_freqs['feature'] = ref_freqs.drop(['position', 'total'], axis = 1).idxmax(axis = 1)
  ref_freqs = ref_freqs[['position', 'feature', 'total']]
  ref_freqs['score'] = 0
  ref_freqs['group_name'] = 'Most common feature'
  ref_freqs['group'] = 'ref-modal'
  return ref_freqs

def format_bits_for_viz(bits):
  # Translate human readable codes to IUPAC codes and tooltip labels
  bits['label'] = bits.feature.apply(lambda x: HUMAN_LABELS[x] if x in HUMAN_LABELS else x)
  bits['feature'] = bits.feature.apply(lambda x: IUPAC_CODES[x] if x in IUPAC_CODES else x)

  # Format data for d3
  groups = [('ref-cons', 'Reference consensus'), ('ref-modal', 'Most common feature')]
  groups = groups + [(group[0], group[1]) for group in bits.loc[bits.group.str.contains('group'), ['group', 'group_name']].drop_duplicates().set_index('group').itertuples()]
  bits = bits[bits.position.isin(BITCHART_POSITIONS)].to_dict(orient = 'index')
  plot_data = {'bits': bits, 'groups': groups}
  return plot_data

def parse_parsetree(parsetree_fh):
  positions = {4: '73', 5: '1:72', 6: '2:71', 7: '3:70', 8: '4:69', 9: '5:68', 10: '6:67', 11: '7:66', 12: '8', 13: '9', 18: '10:25', 19: '11:24', 20: '12:23', 21: '13:22', 22: '14', 23: '15', 24: '16', 25: '17', 26: '17a', 27: '18', 28: '19', 29: '20', 30: '20a', 31: '20b', 32: '21', 35: '26', 36: '27:43', 37: '28:42', 38: '29:41', 39: '30:40', 40: '31:39', 41: '32', 42: '33', 43: '34', 44: '35', 45: '36', 46: '37', 47: '38', 50: '44', 51: '45', 54: 'V11:V21', 55: 'V12:V22', 56: 'V13:V23', 57: 'V14:V24', 58: 'V15:V25', 59: 'V16:V26', 60: 'V17:V27', 61: 'V1', 62: 'V2', 63: 'V3', 64: 'V4', 65: 'V5', 68: '46', 69: '47', 70: '48', 71: '49:65', 72: '50:64', 73: '51:63', 74: '52:62', 75: '53:61', 76: '54', 77: '55', 78: '56', 79: '57', 80: '58', 81: '59', 82: '60'}
  skip_positions = [0, 1, 2, 3, 14, 15, 16, 17, 33, 34, 48, 49, 52, 53, 66, 67]
  terminal_position = 83

  # load parsetrees into memory
  parsetrees = {}
  scores = {}
  identities = {}
  doneParsingHeader = False
  for line in parsetree_fh:
    if line[0] == '>':
      seqname = line.strip()[1:]
      continue
    elif line[0:2] == '//':
      parsetrees[seqname] = (identities, scores)
      # reset everything that might have changed
      positions = {4: '73', 5: '1:72', 6: '2:71', 7: '3:70', 8: '4:69', 9: '5:68', 10: '6:67', 11: '7:66', 12: '8', 13: '9', 18: '10:25', 19: '11:24', 20: '12:23', 21: '13:22', 22: '14', 23: '15', 24: '16', 25: '17', 26: '17a', 27: '18', 28: '19', 29: '20', 30: '20a', 31: '20b', 32: '21', 35: '26', 36: '27:43', 37: '28:42', 38: '29:41', 39: '30:40', 40: '31:39', 41: '32', 42: '33', 43: '34', 44: '35', 45: '36', 46: '37', 47: '38', 50: '44', 51: '45', 54: 'V11:V21', 55: 'V12:V22', 56: 'V13:V23', 57: 'V14:V24', 58: 'V15:V25', 59: 'V16:V26', 60: 'V17:V27', 61: 'V1', 62: 'V2', 63: 'V3', 64: 'V4', 65: 'V5', 68: '46', 69: '47', 70: '48', 71: '49:65', 72: '50:64', 73: '51:63', 74: '52:62', 75: '53:61', 76: '54', 77: '55', 78: '56', 79: '57', 80: '58', 81: '59', 82: '60'}
      skip_positions = [0, 1, 2, 3, 14, 15, 16, 17, 33, 34, 48, 49, 52, 53, 66, 67]
      terminal_position = 83
      scores = {}
      identities = {}
      doneParsingHeader = False
      continue
    elif line[0:3] == '---':
      continue

    cols = line.strip().split()
    if len(cols) > 0 and cols[0] == '0':
      doneParsingHeader = True
      tsc = float(cols[8])
      continue
    if not doneParsingHeader:
      continue

    # parse row. columns: rowid, emitl, emitr, state, mode, nxtl, nxtr, prv, tsc, esc
    rowid = int(cols[0])
    emitl = cols[1]
    emitr = cols[2]
    state = cols[3]
    prev_tsc = tsc
    tsc = float(cols[8])
    esc = float(cols[9])

    # exit on terminal node
    if rowid >= terminal_position:
      continue

    # skip special node rows
    if rowid in skip_positions:
      tsc = float(cols[8])
      continue

    # add standard match positions to scores dict
    if state[-2:] in ["MR", "ML", "MP"]:
      scores[positions[rowid]] = prev_tsc + esc
      if state[-2:] == "MR": identities[positions[rowid]] = re.findall('[A-Z]', emitr)[0]
      if state[-2:] == "ML": identities[positions[rowid]] = re.findall('[A-Z]', emitl)[0]
      if state[-2:] == "MP": identities[positions[rowid]] = '{}:{}'.format(re.findall('[A-Z]', emitl)[0], re.findall('[A-Z]', emitr)[0])

    # for deletions, don't add the esc value
    if state[-1] == "D":
      scores[positions[rowid]] = prev_tsc
      identities[positions[rowid]] = '-'
      if ':' in positions[rowid]: identities[positions[rowid]] = '-:-'
      
    # for insertions, increment remaining positions by 1 and skip
    if state[-2:] in ["IL", "IR"]:
      terminal_position += 1
      for position in sorted(positions, reverse = True):
        if position < rowid: break
        positions[position + 1] = positions.pop(position)

      for i, position in reversed(list(enumerate(sorted(skip_positions)))):
        if position < rowid: break
        skip_positions[i] += 1
  
  bits = []
  for seqname in parsetrees.keys():
    identities, scores = parsetrees[seqname]
    for position in sorted(scores):
      bits.append({
        'seqname': seqname,
        'position': position,
        'score': round(scores[position], 2),
        'feature': identities[position]})

  return bits

