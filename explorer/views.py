from django.shortcuts import render, redirect
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages

import os
import re
import json
from collections import defaultdict
import pandas as pd
from tempfile import NamedTemporaryFile
from shutil import copy
from Bio import SeqIO
import subprocess

from django_pandas.io import read_frame

from django.conf import settings
from . import models
from . import forms
from . import choices

SINGLE_POSITIONS = [
  '8', '9',
  '14', '15', '16', '17', '17a', '18', '19', '20', '20a', '20b', '21',
  '26',
  '32', '33', '34', '35', '36', '37', '38', 
  '44', '45', '46', '47', '48', 
  '54', '55', '56', '57', '58', '59', '60', 
  '73'
]
PAIRED_POSITIONS = [
  '1:72', '2:71', '3:70', '4:69', '5:68', '6:67', '7:66',
  '10:25', '11:24', '12:23', '13:22', 
  '27:43', '28:42', '29:41', '30:40', '31:39', 
  '49:65', '50:64', '51:63', '52:62', '53:61'
]
TERTIARY_INTERACTIONS = ['8:14', '9:23', '10:45', '15:48', '18:55', '19:56', '22:46', '26:44', '54:58']
VARIABLE_LOOP_POSITIONS = ['V1', 'V2', 'V3', 'V4', 'V5', 'V11:V21', 'V12:V22', 'V13:V23', 'V14:V24', 'V15:V25', 'V16:V26', 'V17:V27']
POSITIONS = SINGLE_POSITIONS + PAIRED_POSITIONS + VARIABLE_LOOP_POSITIONS + TERTIARY_INTERACTIONS
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
  'Paired': 'N:N', 'Bulge': '', 'Mismatched': 'N|N', 'NN': '', '': ''})
HUMAN_LABELS = {
  'Amino': 'A / C', 'Keto': 'G / U', 'Weak': 'A / U', 'Strong': 'G / C', 
  'B': 'C / G / U', 'H': 'A / C / U', 'D': 'A / G / U', 'V': 'A / C / G', 'N': 'N',
  'PurinePyrimidine': 'Purine:Pyrimidine', 'PyrimidinePurine': 'Pyrimidine:Purine',
  'WobblePair': 'G:U / U:G', 'StrongPair': 'G:C / C:G', 'WeakPair': 'A:U / U:A', 'AminoKeto': 'A:U / C:G', 'KetoAmino': 'G:C / U:A', 
  'Paired': 'Paired', 'Bulge': '-:N / N:-', 'Mismatched': 'Mismatched', 'NN': 'N:N'
}
HUMAN_LABELS.update(SINGLE_FEATURES)
HUMAN_LABELS.update(PAIRED_FEATURES)


ISOTYPES = ['Ala', 'Arg', 'Asn', 'Asp', 'Cys', 'Gln', 'Glu', 'Gly', 'His', 'Ile', 'iMet', 'Leu', 'Lys', 'Met', 'Phe', 'Pro', 'Ser', 'Thr', 'Trp', 'Tyr', 'Val']


def summary(request):  
  clade = 'Saccharomyces (genus)'
  clade_txid = '4930'
  isotype = 'All'
  form = forms.SummaryForm()
  if request.method == 'POST':
    form = forms.SummaryForm(request.POST)
    if form.is_valid():
      for clade_taxid, clade in choices.CLADES:
        if clade_taxid == form['clade'].value(): break
      isotype = form['isotype'].value()

  return render(request, 'explorer/summary.html', {
    'form': form,
    'clade': clade,
    'clade_txid': clade_txid,
    'isotype': isotype
  })

def variation_distribution(request):
  clade_groups = [['4930', '4895'], ['5204']]
  isotypes = ['All']
  positions = ['8', '9', '14', '35', '36', '37', '46', '73', '12:23', '18:55', '11:24']

  form = forms.DistributionForm()
  fields = ['isotypes', 'positions', 'clade_group_1', 'clade_group_2', 'clade_group_3', 'clade_group_4', 'clade_group_5']
  if request.method == "POST":
    # Django doesn't return multiple choice field properly, so need to grab lists manually
    form = forms.DistributionForm({field: request.POST.getlist(field) for field in fields})
    if form.is_valid():
      clade_groups = form.get_clade_groups()
      isotypes = form['isotypes'].value()
      positions = form['positions'].value()

  clade_group_names = []
  for clade_group in clade_groups:
    names = []
    for clade_taxid, clade in choices.CLADES:
      if clade_taxid in clade_group: 
        names.append(clade)
    clade_group_names.append(names)

  return render(request, 'explorer/distribution.html', {
    'form': form,
    'clade_groups': clade_groups,
    'isotypes': isotypes,
    'positions': positions,
    'clade_group_names': clade_group_names
  })

def variation_species(request):
  filter_clades = [{'4895': ('Schizosaccharomyces', 'genus')}, {'4930': ('Saccharomyces', 'genus')}]
  foci = [('Ala', '3:70'), ('Gly', '3:70'), ('Ala', '46'), ('Gly', '46')]

  clade_list = {}
  for taxonomy in models.Taxonomy.objects.values():
    clade_list[taxonomy['taxid']] = taxonomy['name'], taxonomy['rank']

  if request.method == "POST":
    clade_groups = [request.POST.getlist('form_clades_1'), request.POST.getlist('form_clades_2'), request.POST.getlist('form_clades_3'), request.POST.getlist('form_clades_4'), request.POST.getlist('form_clades_5')]
    filter_clades = []
    for clade_group in clade_groups:
      if len(clade_group) == 0: continue
      filter_clades.append({taxid: clade_list[taxid] for taxid in clade_group})

    foci = list(zip(request.POST.getlist('form_isotypes'), request.POST.getlist('form_positions')))
    foci = [focus for focus in foci if focus[0] != '']

  return render(request, 'explorer/species.html', {
    'plot_clades': filter_clades,
    'foci': foci,
    'clade_list': clade_list,
    'isotypes_list': ISOTYPES,
    'positions_list': POSITIONS

  })

def compare(request):
  if request.method != 'POST':
    return render(request, 'explorer/compare.html', {
      'formset': forms.CompareFormSet(),
      'valid_form': False,
      'formset_json': 'none'
    })

  formset = forms.CompareFormSet(request.POST)
  if not formset.is_valid():
    print(formset.errors)

  formset_json_fh = NamedTemporaryFile('w')
  for form in formset:
    print(form.as_dict())

  formset_json_fh.write(json.dumps([form.as_dict() for form in formset]))
  formset_json_fh.flush()
  copy(formset_json_fh.name, settings.MEDIA_ROOT + formset_json_fh.name)
  formset_json_fh.close()

  return render(request, 'explorer/compare.html', {
    'formset': formset,
    'valid_form': True,
    'formset_json': formset_json_fh.name
  })

def bitchart(request, formset_json_filename):
  # get formset
  formset = json.loads(open(settings.MEDIA_ROOT + formset_json_filename).read())
  os.remove(settings.MEDIA_ROOT + formset_json_filename)
  
  # read in all tRNAs
  seqs = []
  seq_file_handle = open(settings.ENGINE_DIR + 'tRNAs.fa')
  for seq in SeqIO.parse(seq_file_handle, 'fasta'):
    seqs.append(seq)
  seq_file_handle.close()

  # write tRNA sets to files
  trna_fasta_files = []
  for i, data in enumerate(formset):
    print('Form {} with dict {}'.format(i, data))

    # Skip dummy form row
    if i == 1: continue 
    
    # Prepare tRNAs for writing to file
    trna_fasta_fh = NamedTemporaryFile('w', buffering = 1)
    trna_seqs = []

    # For selects, query db
    if 'use_fasta' not in data or not data['use_fasta']:
      clade_qs = models.Taxonomy.objects.filter(taxid = data['clade']).values()[0]
      rank, name = clade_qs['rank'] if clade_qs['rank'] != 'class' else 'taxclass', clade_qs['name']
      trna_qs = models.tRNA.objects.filter(Q(**{rank: name})).values('seqname')
      if data['isotype'] != 'All':
        trna_qs = trna_qs.filter(isotype = data['isotype'])
      seqnames = [d['seqname'] for d in trna_qs]
      for seq in seqs:
        if seq.description in seqnames: trna_seqs.append(seq)

      # make sure that there are enough seqs to build a CM with
      if i == 0 and len(trna_qs) < 5:
        raise ValidationError('Not enough sequences in database for reference category. Query a broader set.')

      SeqIO.write(trna_seqs, trna_fasta_fh, 'fasta')
    # otherwise write input directly into file
    else:
      trna_fasta_fh.write(data['fasta'])
    
    trna_fasta_fh.flush()
    trna_fasta_files.append(trna_fasta_fh)

  # Build reference CM model
  ref_fasta = trna_fasta_files[0].name
  ref_align_fh = NamedTemporaryFile()
  num_model = '{}/euk-num.cm'.format(settings.ENGINE_DIR)
  cmd_cmalign = 'cmalign -g --notrunc --matchonly -o {} {} {} > /dev/null'.format(ref_align_fh.name, num_model, ref_fasta)
  res = subprocess.run(cmd_cmalign, shell = True)
  ref_model_fh = NamedTemporaryFile()
  cmd_cmbuild = 'cmbuild --hand --enone -F {} {} > /dev/null'.format(ref_model_fh.name, ref_align_fh.name)
  res = subprocess.run(cmd_cmbuild, shell = True)

  # Get normalizing bit scores. To do this, we generate a consensus sequence and align it to the model.
  # Generate consensus sequence. First, build a consensus model with gaps.
  cons_model_fh = NamedTemporaryFile()
  cons_align_fh = NamedTemporaryFile()
  cons_fasta_fh = NamedTemporaryFile()
  cons_parsetree_fh = NamedTemporaryFile('r+')
  cmd_cmemit = 'cmemit --exp 5 -N 1000 -a {} > {}'.format(ref_model_fh.name, cons_align_fh.name)
  res = subprocess.run(cmd_cmemit, shell = True)
  cmd_cmbuild = 'cmbuild --enone -F {} {} > /dev/null'.format(cons_model_fh.name, cons_align_fh.name)
  res = subprocess.run(cmd_cmbuild, shell = True)
  # Then emit a consensus sequence, format, align to reference model, and get normalizing bits
  cmd_cmemit = 'cmemit -c {}'.format(cons_model_fh.name)
  res = subprocess.run(cmd_cmemit, stdout = subprocess.PIPE, shell = True)
  cons_fasta_fh.write(res.stdout.upper())
  cons_fasta_fh.flush()
  cmd_cmalign = 'cmalign -g --notrunc --matchonly --tfile {} {} {} > /dev/null'.format(cons_parsetree_fh.name, ref_model_fh.name, cons_fasta_fh.name)
  res = subprocess.run(cmd_cmalign, shell = True)
  ref_bits = pd.DataFrame(parse_parsetree(cons_parsetree_fh))
  ref_bits.group = 'Reference consensus'

  # Align tRNAs to reference model and collect bit scores
  bits = pd.DataFrame()
  for i, trna_fasta_fh in enumerate(trna_fasta_files[1:]):
    group_name = formset[i+2]['name']

    num_model_align_fh = NamedTemporaryFile('r+')
    processed_fasta_fh = NamedTemporaryFile('r+', buffering = 1)
    parsetree_fh = NamedTemporaryFile('r+', buffering = 1)

    # Remove introns from all tRNAs (except reference). First, align to numbering model to purge insertions
    cmd_cmalign = 'cmalign -g --notrunc --matchonly -o {} {} {} > /dev/null'.format(num_model_align_fh.name, num_model, trna_fasta_fh.name)
    res = subprocess.run(cmd_cmalign, shell = True)

    # remove introns using alignment and rewrite tRNAs to new file
    for line in num_model_align_fh:
      if line[0] in ['#', '/', '\n']: continue
      seqname, seq = line.strip().split()
      seq = seq.replace('-', '')
      processed_fasta_fh.write('>{}\n{}\n'.format(seqname, seq))

    # realign to reference model and parse parsetree output
    cmd_cmalign = 'cmalign -g --notrunc --matchonly --tfile {} -o /dev/null {} {} > /dev/null'.format(parsetree_fh.name, ref_model_fh.name, processed_fasta_fh.name)
    res = subprocess.run(cmd_cmalign, shell = True)
    current_bits = pd.DataFrame(parse_parsetree(parsetree_fh))
    
    # For selections with mutliple tRNAs, summarize by average score and modal feature
    num_trnas = len(current_bits.seqname.unique())
    modal_features = current_bits.groupby('position').apply(lambda x: x['feature'].mode()[0]).reset_index().rename(columns = {0: 'feature'})
    current_bits = current_bits.set_index(['seqname', 'feature', 'position']).groupby('position').mean()
    current_bits =  current_bits.join(modal_features.set_index('position')).reset_index()
    current_bits = current_bits[['feature', 'position', 'score']]
    current_bits['group'] = group_name
    current_bits['total'] = num_trnas
    bits = bits.append(current_bits)

  # Normalize
  bits['score'] = round(bits.apply(lambda x: x['score'] - ref_bits[ref_bits.position == x['position']]['score'].values[0], axis = 1), 2)
  print(bits.head())

  # Get consensus and modals for reference
  ref_taxid = formset[0]['clade']
  ref_isotype = formset[0]['isotype']
  ref_cons_qs = models.Consensus.objects.filter(taxid = ref_taxid, isotype = ref_isotype).values()
  ref_cons = read_frame(ref_cons_qs).drop(['id', 'taxid', 'isotype'], axis = 1).stack().unstack(0).reset_index()
  ref_cons.columns = ['position', 'feature']
  ref_cons.position = ref_cons.position.apply(lambda x: x[1:].replace('_', ':'))
  ref_cons['score'] = 0
  ref_cons['total'] = ''
  ref_cons['group'] = 'Reference consensus'
  
  freqs_qs = models.Freq.objects.filter(taxid = ref_taxid, isotype = ref_isotype).values()
  ref_freqs = read_frame(freqs_qs).drop(['id', 'taxid', 'isotype'], axis = 1)
  ref_freqs['feature'] = ref_freqs.drop(['position', 'total'], axis = 1).idxmax(axis = 1)
  ref_freqs = ref_freqs[['position', 'feature', 'total']]
  ref_freqs['score'] = 0
  ref_freqs['group'] = 'Most common feature'

  bits = pd.concat([bits, ref_cons, ref_freqs], sort = True).reset_index(drop = True)
  
  # Translate human readable codes to IUPAC codes and tooltip labels
  bits['label'] = bits.feature.apply(lambda x: HUMAN_LABELS[x] if x in HUMAN_LABELS else x)
  bits['feature'] = bits.feature.apply(lambda x: IUPAC_CODES[x] if x in IUPAC_CODES else x)

  groups = ['Reference consensus', 'Most common feature'] + list(filter(lambda x: x not in ['Reference consensus', 'Most common feature'], bits.group.unique()))
  bits = bits[bits.position.isin(SINGLE_POSITIONS + PAIRED_POSITIONS)].to_dict(orient = 'index')

  plot_data = {'bits': bits, 'groups': groups}

  return JsonResponse(json.dumps(plot_data), safe = False)

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

