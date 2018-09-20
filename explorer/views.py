from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings

import json
from tempfile import NamedTemporaryFile
from shutil import copy

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
      clade_taxid = ''
      clade = ''
      for clade_txid, clade in choices.CLADES:
        if clade_txid == form['clade'].value():
          break
      isotype = form['isotype'].value()

  return render(request, 'explorer/summary.html', {
    'form': form,
    'clade': clade,
    'clade_txid': clade_txid,
    'isotype': isotype
  })

def variation_distribution(request):
  clade_groups = [['4930', '4895'], ['5204']]
  clade_group_names = [['Saccharomyces (genus)', 'Schizosaccharomyces (genus)'], ['Basidiomycota (phylum)']]
  isotypes = ['All']
  positions = ['8', '9', '14', '35', '36', '37', '46', '73', '12:23', '18:55', '11:24']
  form_clade_values = []

  form = forms.DistributionForm()
  if request.method == "POST":
    form = forms.DistributionForm(request.POST)
    if form.is_valid():
      clade_groups = form.get_clade_groups()
      isotypes = form['isotypes'].value()
      positions = form['positions'].value()
      clade_group_names = form.get_clade_group_names()

  return render(request, 'explorer/distribution.html', {
    'form': form,
    'clade_groups': clade_groups,
    'isotypes': isotypes,
    'positions': positions,
    'clade_group_names': clade_group_names

  })

def variation_species(request):
  clade_groups = [['4930', '4895'], ['5204']]
  clade_group_names = [['Saccharomyces (genus)', 'Schizosaccharomyces (genus)'], ['Basidiomycota (phylum)']]
  foci = [('Ala', '3:70'), ('Gly', '3:70'), ('Ala', '46'), ('Gly', '46')]

  form = forms.SpeciesDistributionForm()
  
  if request.method == "POST":
    form = forms.SpeciesDistributionForm(request.POST)
    if form.is_valid():
      clade_groups = form.get_clade_groups()
      foci = form.get_foci()
      clade_group_names = form.get_clade_group_names()

  return render(request, 'explorer/species.html', {
    'form': form,
    'clade_groups': clade_groups,
    'foci': foci,
    'clade_group_names': clade_group_names
  })

def compare(request):
  if request.method != 'POST':
    return render(request, 'explorer/compare.html', {
      'formset': forms.CompareFormSet(),
      'valid_form': False,
      'formset_json': 'none'
    })

  formset = forms.CompareFormSet(request.POST)
  formset_json_fh = NamedTemporaryFile('w')

  if formset.is_valid():
    formset_json_fh.write(json.dumps([form.as_dict() for form in formset]))
    formset_json_fh.flush()
    copy(formset_json_fh.name, settings.MEDIA_ROOT + formset_json_fh.name)
  formset_json_fh.close()

  return render(request, 'explorer/compare.html', {
    'formset': formset,
    'valid_form': True,
    'formset_json': formset_json_fh.name
  })
