from django import template
from django.utils.safestring import mark_safe


# register is an object that helps us register new tags
register = template.Library()

@register.filter('clade_dicts_to_url_string')
def clade_dicts_to_url_string(clade_dicts):
  return ';'.join([','.join([tax_id for tax_id in clade_dict]) for clade_dict in clade_dicts])

@register.filter('clade_dicts_to_pretty_string')
def clade_dicts_to_pretty_string(clade_dicts):
  groups_str = []
  for i, clade_dict in enumerate(clade_dicts):
    groups_str.append('Group {}: {}'.format(i + 1, ', '.join(['{} ({})'.format(clade, rank) for clade, rank in clade_dict.values()])))
  return '\n'.join(groups_str)

@register.filter('list_to_url_string')
def list_to_url_string(mylist):
  return ','.join(mylist)

@register.filter('list_to_pretty_string')
def list_to_pretty_string(mylist):
  return ', '.join(mylist)

@register.filter('foci_to_url_string')
def foci_to_url_string(foci):
  return ';'.join([','.join(focus) for focus in foci])

@register.filter('foci_to_pretty_string')
def foci_to_pretty_string(foci):
  return '\n'.join([', '.join(focus) for focus in foci])


@register.filter('minus1')
def minus1(number):
  return number - 1