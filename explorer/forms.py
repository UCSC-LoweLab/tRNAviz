from django import forms
from django.forms import formset_factory
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.utils.html import escape

import re

from . import choices

class SummaryForm(forms.Form):
  clade = forms.ChoiceField(
    widget = forms.Select({'class': 'form-control multiselect isotype-select'}),
    choices = choices.CLADES,
    required = True,
    initial = '4930')
  isotype = forms.ChoiceField(
    widget = forms.Select({'class': 'form-control multiselect isotype-select'}), 
    initial = 'All',
    choices = choices.ISOTYPES,
    required = True)

class CladeGroupForm(forms.Form):
  '''Abstract for any forms that use clade groups'''
  def get_clade_groups(self):
    clade_groups = []
    for i in range(1, 6):
      clade_group = self['clade_group_{}'.format(i)].value()
      if clade_group is not None and len(clade_group) > 0:
        clade_groups.append(clade_group)
    return clade_groups

  def get_clade_group_names(self):
    clade_group_names = []
    for clade_group in self.get_clade_groups():
      names = []
      for clade_taxid, clade in choices.CLADES:
        if clade_taxid in clade_group: 
          names.append(clade)
      clade_group_names.append(names)
    return clade_group_names

  def clean(self):
    if len(self.get_clade_groups()) == 0:
      raise ValidationError('no clades specified')

class DistributionForm(CladeGroupForm):
  clade_group_1 = forms.CharField(widget = forms.SelectMultiple({'class': 'form-control multiselect clade-group-select'}), required = False)
  clade_group_2 = forms.CharField(widget = forms.SelectMultiple({'class': 'form-control multiselect clade-group-select'}), required = False)
  clade_group_3 = forms.CharField(widget = forms.SelectMultiple({'class': 'form-control multiselect clade-group-select'}), required = False)
  clade_group_4 = forms.CharField(widget = forms.SelectMultiple({'class': 'form-control multiselect clade-group-select'}), required = False)
  clade_group_5 = forms.CharField(widget = forms.SelectMultiple({'class': 'form-control multiselect clade-group-select'}), required = False)
  isotypes = forms.MultipleChoiceField(
    widget = forms.SelectMultiple({'class': 'form-control multiselect isotype-select'}),
    initial = 'All',
    choices = choices.ISOTYPES,
    required = True)
  positions = forms.MultipleChoiceField(
    widget = forms.SelectMultiple({'class': 'form-control multiselect isotype-select'}),
    initial = 'single',
    choices = choices.POSITIONS,
    required = True)

  def as_dict(self):
    return {
      'clade_groups': self.get_clade_groups(),
      'isotypes': self['isotypes'].value(),
      'positions': self['positions'].value(),
    }

class FocusWidget(forms.MultiWidget):
  def __init__(self,*args,**kwargs):
    widgets = (
      forms.Select({'class': 'form-control multiselect isotype-select'}, choices = choices.ISOTYPES_DISTINCT), 
      forms.Select({'class': 'form-control multiselect position-select'}, choices = choices.POSITIONS_DISTINCT)
    )
    super(FocusWidget, self).__init__(widgets, *args, **kwargs)
  
  def decompress(self, value):
    return [value[0], value[1]] if value else [None, None]

  def format_output(self, rendered_widgets):
    return ''.join(rendered_widgets)

  def render(self, name, value, attrs=None):
    if self.is_localized:
      for widget in self.widgets:
        widget.is_localized = self.is_localized
    if not isinstance(value, list):
        value = self.decompress(value)
    output = []
    final_attrs = self.build_attrs(attrs)
    id_ = final_attrs.get('id', None)
    for i, widget in enumerate(self.widgets):
        try: widget_value = value[i]
        except IndexError: widget_value = None
        if id_: final_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
        output.append(widget.render(name + '_%s' % i, widget_value, final_attrs))
    # Original:
    # return mark_safe(self.format_output(output))
    # Only this line was written by myself:
    return {'isotype': mark_safe(self.format_output(output[0])), 'position': mark_safe(self.format_output(output[1]))}

class FocusField(forms.MultiValueField):
  widget = FocusWidget

  def __init__(self, *args, **kwargs):
    fields = (
      forms.ChoiceField(choices = choices.ISOTYPES_DISTINCT),
      forms.ChoiceField(choices = choices.POSITIONS_DISTINCT)
    )
    super(FocusField, self).__init__(fields, required = False, *args, **kwargs)

  def compress(self, data_list):
    if data_list:
      if data_list[0] in self.empty_values:
          raise ValidationError('did not select an isotype/position pair', code = 'invalid_isotype')
      if data_list[1] in self.empty_values:
          raise ValidationError('did not select an isotype/position pair', code = 'invalid_position')
      return tuple(data_list)
    return None

class SpeciesDistributionForm(CladeGroupForm):
  clade_group_1 = forms.CharField(widget = forms.SelectMultiple({'class': 'form-control multiselect clade-group-select'}), required = False)
  clade_group_2 = forms.CharField(widget = forms.SelectMultiple({'class': 'form-control multiselect clade-group-select'}), required = False)
  clade_group_3 = forms.CharField(widget = forms.SelectMultiple({'class': 'form-control multiselect clade-group-select'}), required = False)
  clade_group_4 = forms.CharField(widget = forms.SelectMultiple({'class': 'form-control multiselect clade-group-select'}), required = False)
  clade_group_5 = forms.CharField(widget = forms.SelectMultiple({'class': 'form-control multiselect clade-group-select'}), required = False)
  focus_1 = FocusField()
  focus_2 = FocusField()
  focus_3 = FocusField()
  focus_4 = FocusField()
  focus_5 = FocusField()

  def get_foci(self):
    foci = []
    for i in range(1, 6):
      isotype, position = self['focus_{}'.format(i)].value()
      if isotype is not None and position is not None and isotype != '' and position != '':
        foci.append((isotype, position))
    return foci

  def clean(self):
    super().clean()
    # Make sure at least one focus is listed
    if len(self.get_foci()) == 0:
      raise forms.ValidationError('no foci specified')


class CompareForm(forms.Form):
  name = forms.CharField(widget = forms.TextInput({
    'class': 'form-control name-input',
    'placeholder': 'Group name'
    }), max_length = 20, required = False)
  fasta = forms.CharField(widget = forms.Textarea({
    'class': 'form-control fasta-input',
    'placeholder': 'Paste tRNAs in FASTA format'
    }), required = False)
  clade = forms.ChoiceField(choices = choices.CLADES, required = False)
  isotype = forms.ChoiceField(
    widget = forms.Select({'class': 'form-control multiselect isotype-select'}), 
    initial = 'All',
    choices = choices.ISOTYPES,
    required = False)
  use_fasta = forms.BooleanField(
    widget = forms.CheckboxInput(attrs = {
      'class': 'use-fasta-toggle',
      'data-toggle': 'toggle',
      'data-size': 'small',
      'data-onstyle': 'info',
      'data-offstyle': 'secondary',
      'data-on': 'Switch to data select',
      'data-off': 'Switch to FASTA input'
      }), 
    required = False)

  def as_dict(self):
    return {
      'name': str(self['name'].value()),
      'fasta': str(self['fasta'].value()),
      'clade': str(self['clade'].value()),
      'isotype': str(self['isotype'].value()),
      'use_fasta': bool(self['use_fasta'].value())
    }


  def _clean_fields(self):
    # validate fields, but only validation fasta sequence if necessary
    # by default, clade and isotype will always be validated. This should not be a problem unless you hack the POST request. And why would you do that?
    for name, field in self.fields.items():
      if name == 'fasta':
        # save value for later
        fasta = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
        continue
      value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(name))
      try:
        value = field.clean(value)
        self.cleaned_data[name] = value
        if hasattr(self, 'clean_%s' % name):
          value = getattr(self, 'clean_%s' % name)()
          self.cleaned_data[name] = value
      except ValidationError as e:
        self.add_error(name, e)

    if self.cleaned_data['use_fasta']:
      try:
        # perform regular validation first
        self.cleaned_data['fasta'] = self.fields['fasta'].clean(fasta)
        self.check_fasta(self.cleaned_data['fasta'])
      except ValidationError as e:
        self.add_error('fasta', e)
    else:
      self.cleaned_data['fasta'] = fasta
      # Do a final validation to make sure clade / isotype aren't empty values
      if 'clade' in self.cleaned_data:
        if self.cleaned_data['clade'] == '':
          self.add_error('clade', 'Please make a selection for both clade and isotype fields')
      if 'isotype' in self.cleaned_data:
        if self.cleaned_data['isotype'] == '':
          self.add_error('isotype', 'Please make a selection for both clade and isotype fields')


  # Easier than overloading a CharField
  def check_fasta(self, input_str):
    lines = iter(input_str.split('\n'))
    while True:
      # Skip any text before the first record (e.g. blank lines, comments) 
      try:
        line = next(lines)
      except StopIteration:
        raise ValidationError('Malformed input FASTA')
      if line == "":
        raise ValidationError('Input FASTA is empty')
      elif line[0] == '>':
        break
      else:
        raise ValidationError('Malformed input FASTA')
    while True:
      description = line[1:].rstrip()
      seq = ''
      try:
        line = next(lines)
      except StopIteration:
        raise ValidationError('Malformed input FASTA')
      while True:
        if not line or line[0] == ">":
          break
        seq += line.rstrip()
        try:
          line = next(lines)
        except StopIteration:
          line = False
      seq = seq.replace(" ", "").replace('\r', "")  
      if len(seq) == 0:
        raise ValidationError('Detected empty sequence for: {}'.format(description))
      bad_chars = re.findall('[^agctuAGCTU]', seq)
      if len(bad_chars) != 0:
        bad_char_html = ', '.join(['<code>{}</code>'.format(escape(letter)) for letter in sorted(list(set(bad_chars)))])
        raise ValidationError('Input sequence may not contain the following characters: {}'.format(bad_char_html))
      if not line:
        return True

class EmptyPermittedFormSet(forms.BaseFormSet):
  def __init__(self, *args, **kwargs):
    super(EmptyPermittedFormSet, self).__init__(*args, **kwargs)
    for form in self.forms:
      form.empty_permitted = False

CompareFormSet = formset_factory(CompareForm, formset = EmptyPermittedFormSet, can_delete = True, extra = 3)