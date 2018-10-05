from django import template
from django.utils.safestring import mark_safe
from django.db.models import Max, Min

from .. import choices
from .. import models

# register is an object that helps us register new tags
register = template.Library()

@register.filter('clade_groups_to_url_string')
def clade_groups_to_url_string(clade_groups):
  return ';'.join([','.join([tax_id for tax_id in clade_group]) for clade_group in clade_groups])

@register.filter('index')
def index(List, i):
  if int(i) < len(List):
    return List[int(i)]
  else:
    return None

@register.filter('clade_names_to_pretty_string')
def clade_names_to_pretty_string(clade_group_names):
  groups_str = []
  for i, names in enumerate(clade_group_names):
    groups_str.append('Group {}: {}'.format(i + 1, ', '.join(names)))
  return '\n'.join(groups_str)

@register.filter('list_to_url_string')
def list_to_url_string(mylist):
  return ','.join(mylist)

@register.filter('list_to_pretty_string')
def list_to_pretty_string(mylist):
  return ', '.join(mylist)

@register.filter('foci_to_url_string')
def foci_to_url_string(foci):
  focus_strings = []
  for focus in foci:
    focus_strings.append('{},{},{},{},{}'.format(focus['position'], focus['isotype'], focus['anticodon'], focus['score_min'], focus['score_max']))    
  return ';'.join(focus_strings)

@register.filter('minus2')
def minus2(number):
  return number - 2

@register.filter('parity_to_div_class')
def parity_to_div_class(number):
  if number % 2 == 0: return 'select-bar-even'
  else: return 'select-bar-odd'

@register.filter('clade_lookup')
def clade_lookup(taxid):
  for clade_taxid, clade in choices.CLADES:
   if clade_taxid == taxid: return clade
  return ''

@register.filter('haserrors')
def haserrors(formset, formset_type):
  for i, errordict in enumerate(formset.errors):
    if formset_type == 'compare' and i < 2: continue
    elif i < 1: continue
    if len(errordict) > 0:
      return True
  if len(formset.non_form_errors()) > 0:
    return True
  return False

@register.simple_tag
def score_range():
  return '{} - {}'.format(models.tRNA.objects.aggregate(Min('score'))['score__min'], models.tRNA.objects.aggregate(Max('score'))['score__max'])

@register.filter('focus_value')
def focus_value(focus, key):
  if key == 'score':
    return '{} - {}'.format(focus['score_min'], focus['score_max'])
  return focus[key]