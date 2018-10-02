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
    trna_form = forms.tRNAForm(request.POST)
    if form.is_valid():
      clade_groups = form.get_clade_groups()
      foci = form.get_foci()
      clade_group_names = form.get_clade_group_names()

  print(request.POST)
  return render(request, 'explorer/species.html', {
    'form': form,
    'clade_groups': clade_groups,
    'foci': foci,
    'clade_group_names': clade_group_names,
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
    valid_form = True
  else:
    valid_form = False

  formset_json_fh.close()
  formset.formset_wide_errors = formset._non_form_errors
  return render(request, 'explorer/compare.html', {
    'formset': formset,
    'valid_form': valid_form,
    'formset_json': formset_json_fh.name
  })
