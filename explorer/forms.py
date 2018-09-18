from django import forms
from django.forms import formset_factory
from . import choices
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError

class SummaryForm(forms.Form):
  clade = forms.ChoiceField(
    widget = forms.Select({'class': 'form-control multiselect isotype-select'}),
    choices = choices.CLADES,
    required = True,
    initial = '')
  isotype = forms.ChoiceField(
    widget = forms.Select({'class': 'form-control multiselect isotype-select'}), 
    initial = 'All',
    choices = choices.ISOTYPES,
    required = True)

class CladeGroupField(forms.MultipleChoiceField):
  def __init__(self, *args, **kwargs):
    super(CladeGroupField, self).__init__(*args, **kwargs)
    self.widget = forms.SelectMultiple({'class': 'form-control multiselect clade-group-select'})
    self.choices = choices.CLADES
    self.required = False

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
    return self.cleaned_data

class DistributionForm(CladeGroupForm):
  clade_group_1 = CladeGroupField()
  clade_group_2 = CladeGroupField()
  clade_group_3 = CladeGroupField()
  clade_group_4 = CladeGroupField()
  clade_group_5 = CladeGroupField()
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
          raise ValidationError('Did not select an isotype/position pair', code = 'invalid_isotype')
      if data_list[1] in self.empty_values:
          raise ValidationError('Did not select an isotype/position pair', code = 'invalid_position')
      return tuple(data_list)
    return None

class SpeciesDistributionForm(CladeGroupForm):
  clade_group_1 = CladeGroupField()
  clade_group_2 = CladeGroupField()
  clade_group_3 = CladeGroupField()
  clade_group_4 = CladeGroupField()
  clade_group_5 = CladeGroupField()
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

class EmptyPermittedFormSet(forms.BaseFormSet):
  def __init__(self, *args, **kwargs):
    super(EmptyPermittedFormSet, self).__init__(*args, **kwargs)
    for form in self.forms:
      form.empty_permitted = False

CompareFormSet = formset_factory(CompareForm, formset = EmptyPermittedFormSet, can_delete = True, extra = 3)