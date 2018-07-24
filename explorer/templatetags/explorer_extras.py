from django import template
from django.utils.safestring import mark_safe


# register is an object that helps us register new tags
register = template.Library()

# @register.filter('markdown_to_html')
# def markdown_to_html(markdown_text):
#   '''Converts markdown text HTML'''
#   html = mark_safe(markdown2.markdown(markdown_text))
#   return(html)

@register.filter('clade_dict_to_url_string')
def clade_dict_to_url_string(clade_dict):
  return ','.join([tax_id for tax_id in clade_dict])

@register.filter('clade_dict_to_pretty_string')
def clade_dict_to_pretty_string(clade_dict):
  return ', '.join(['{} ({})'.format(clade, rank) for clade, rank in clade_dict.values()])

@register.filter('list_to_url_string')
def list_to_url_string(mylist):
  return ','.join(mylist)

@register.filter('list_to_pretty_string')
def list_to_pretty_string(mylist):
  return ', '.join(mylist)