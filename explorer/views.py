from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.http import HttpResponse

import json
import logging
import os
import uuid

logger = logging.getLogger(__name__)

from . import models
from . import forms
from . import choices
from . import tree
from . import services

def summary(request):
  clade = 'Saccharomyces (genus)'
  clade_txid = '4930'
  isotype = 'Ala'
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

  form = forms.DistributionForm()
  clade_formset = forms.CladeGroupFormSet(prefix = 'clade')

  if request.method == "POST":
    form = forms.DistributionForm(request.POST)
    clade_formset = forms.CladeGroupFormSet(request.POST, prefix = 'clade')
    if form.is_valid():
      isotypes = form['isotypes'].value()
      positions = form['positions'].value()
    if clade_formset.is_valid():
      clade_groups = clade_formset.get_clade_groups()
      clade_group_names = clade_formset.get_clade_group_names()

  clade_formset.formset_wide_errors = clade_formset._non_form_errors
  return render(request, 'explorer/distribution.html', {
    'form': form,
    'clade_formset': clade_formset,
    'clade_groups': clade_groups,
    'isotypes': isotypes,
    'positions': positions,
    'clade_group_names': clade_group_names

  })

def variation_species(request):
  clade_groups = [['4930', '4895'], ['5204']]
  clade_group_names = [['Saccharomyces (genus)', 'Schizosaccharomyces (genus)'], ['Basidiomycota (phylum)']]
  foci = [{'position': '3:70', 'isotype': 'Gly', 'anticodon': 'All', 'score_min': '25', 'score_max': '100.1'}, 
      {'position': '3:70', 'isotype': 'Asn', 'anticodon': 'All', 'score_min': '35', 'score_max': '110'}]

  clade_formset = forms.CladeGroupFormSet(prefix = 'clade')
  focus_formset = forms.FocusFormSet(prefix = 'focus')

  if request.method == "POST":
    clade_formset = forms.CladeGroupFormSet(request.POST, prefix = 'clade')
    focus_formset = forms.FocusFormSet(request.POST, prefix = 'focus')
    if clade_formset.is_valid():
      clade_groups = clade_formset.get_clade_groups()
      clade_group_names = clade_formset.get_clade_group_names()
    if focus_formset.is_valid():
      foci = focus_formset.get_foci()

  clade_formset.formset_wide_errors = clade_formset._non_form_errors
  focus_formset.formset_wide_errors = focus_formset._non_form_errors
  return render(request, 'explorer/species.html', {
    'clade_formset': clade_formset,
    'focus_formset': focus_formset,
    'clade_groups': clade_groups,
    'foci': foci,
    'clade_group_names': clade_group_names,
  })

def compare(request):
  compare_list = [{"fasta": "None", "clade": "2251", "isotype": "All", "domain": "None", "name": "None", "use_fasta": "False"},
                  {"fasta": "", "clade": "2207", "isotype": "All", "domain": "Universal", "name": "", "use_fasta": "False"}]

  if request.method != 'POST':
    formset = forms.CompareFormSet()
    return render(request, 'explorer/compare.html', {
      'formset': formset,
      'valid_form': True,
      'compare_list': compare_list,
      'formset_json': 'default'
    })

  formset = forms.CompareFormSet(request.POST)
  formset_json_name = str(uuid.uuid4())
  valid_form = False

  if formset.is_valid():
    formset_json_path = os.path.join(settings.MEDIA_ROOT, formset_json_name)
    os.makedirs(os.path.dirname(formset_json_path), exist_ok=True)
    with open(formset_json_path, 'w') as f:
      f.write(json.dumps([form.as_dict() for form in formset]))
    valid_form = True
    compare_list = formset.get_compare_list()

  formset.formset_wide_errors = formset._non_form_errors
  return render(request, 'explorer/compare.html', {
    'formset': formset,
    'valid_form': valid_form,
    'compare_list': compare_list,
    'formset_json': formset_json_name
  })

def about(request):
  return render(request, 'explorer/about.html')

def taxonomy(request):
  phylogeny = tree.full_tree.root.makeIterable()
  return render(request, 'explorer/taxonomy.html', {
    'tree': phylogeny
  })

def visualize_itol(request, taxonomy_id):
  newick_tree = services.newick_tree(taxonomy_id)
  if not newick_tree.endswith(';'):
    newick_tree += ';'
  return render(request, 'explorer/itol_redirect.html', {
    'newick_tree': newick_tree,
  })
