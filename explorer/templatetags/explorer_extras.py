from django import template
from django.utils.safestring import mark_safe


# register is an object that helps us register new tags
register = template.Library()

# @register.filter('markdown_to_html')
# def markdown_to_html(markdown_text):
#   '''Converts markdown text HTML'''
#   html = mark_safe(markdown2.markdown(markdown_text))
#   return(html)

@register.filter('clade_dicts_to_url_string')
def clade_dicts_to_url_string(clade_dicts):
  return ';'.join([','.join([tax_id for tax_id in clade_dict]) for clade_dict in clade_dicts])
# @register.simple_tag
# def clade_groups_to_url_string(group1, group2, group3, group4, group5):
#   print('here')
#   print([group1, group2, group3, group4, group5])
#   print(group2)
#   print('3')
#   print(group3)
#   groups = []
#   for group in [group1, group2, group3, group4, group5]:
#     group_url_string = ','.join(group)
#     if group_url_string != '':
#       groups.append(group_url_string)
#   print('2')
#   print(groups)
#   return ';'.join(groups)


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