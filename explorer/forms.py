from django import forms
from django.forms import formset_factory
from . import models
from . import choices

CLADES = [(clade.taxid, '{} ({})'.format(clade.name, clade.rank)) for clade in models.Taxonomy.objects.all()]

class CompareForm(forms.Form):
  name = forms.CharField(widget = forms.TextInput({
    'class': 'form-control name-input',
    'placeholder': 'Group name'
    }), max_length = 20, required = False)
  fasta = forms.CharField(widget = forms.Textarea({
    'class': 'form-control fasta-input',
    'placeholder': 'Paste tRNAs in FASTA format'
    }), required = False)
  clade = forms.ChoiceField(choices = CLADES, required = False)
  isotype = forms.ChoiceField(
    widget = forms.Select({'class': 'form-control multiselect isotype-select'}), 
    initial = 'All',
    choices = choices.ISOTYPES,
    required = False)
  use_fasta = forms.BooleanField(widget = forms.CheckboxInput(attrs = {
    'class': 'use-fasta-toggle',
    'data-toggle': 'toggle',
    'data-size': 'small',
    'data-onstyle': 'info',
    'data-offstyle': 'secondary',
    'data-on': 'Switch to data select',
    'data-off': 'Switch to FASTA input'
    }), required = False)

  def is_valid(self):
    valid = super(CompareForm, self).is_valid()
    if not valid: return valid

    # validate clade
    # try:
    #   clade = models.Taxonomy.objects.get(taxid = self.cleaned_data['clade'])
    # except models.Taxonomy.DoesNotExist:
    #   self.add_error('clade', 'Invalid clade - does not exist in database')
    #   return False

    return True

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