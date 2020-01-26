from django import forms
from django.forms import formset_factory
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django.db.models import Max, Min

import re

from . import choices
from . import compare
from . import models

class SummaryForm(forms.Form):
  clade = forms.ChoiceField(
    widget = forms.Select({'class': 'form-control multiselect clade-select'}),
    choices = choices.CLADES,
    required = True,
    initial = '4930')
  isotype = forms.ChoiceField(
    widget = forms.Select({'class': 'form-control multiselect isotype-select'}), 
    initial = 'Ala',
    choices = choices.ISOTYPES,
    required = True)

class DummyFormSet(forms.BaseFormSet):
  def __init__(self, dummy_form_index = 1, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.dummy_form_index = dummy_form_index

  # Need to overload is_valid and full_clean to skip dummy form during validation
  def is_valid(self):
    if not self.is_bound:
      return False
    forms_valid = True
    self.errors
    for i in range(0, self.total_form_count()):
      form = self.forms[i]
      if self.can_delete and self._should_delete_form(form):
        continue
      is_valid = form.is_valid()
      if i == self.dummy_form_index: continue
      forms_valid &= is_valid
    return forms_valid and not self.non_form_errors()

  def full_clean(self):
    """
    Clean all of self.data and populate self._errors and
    self._non_form_errors.
    """
    self._errors = []
    self._non_form_errors = self.error_class()
    empty_forms_count = 0

    if not self.is_bound:  # Stop further processing.
      return
    for i in range(0, self.total_form_count()):
      form = self.forms[i]
      # Empty forms are unchanged forms beyond those with initial data.
      if not form.has_changed() and i >= self.initial_form_count():
        empty_forms_count += 1
      # Accessing errors calls full_clean() if necessary.
      # _should_delete_form() requires cleaned_data.
      form_errors = form.errors
      if i == self.dummy_form_index: 
        form_errors = {}
      if self.can_delete and self._should_delete_form(form):
        continue
      self._errors.append(form_errors)

    try:
      if (self.validate_max and self.total_form_count() - len(self.deleted_forms) > self.max_num) or \
          self.management_form.cleaned_data['TOTAL_FORMS'] > self.absolute_max:
        raise ValidationError(ngettext(
          "Please submit %d or fewer forms.",
          "Please submit %d or fewer forms.", self.max_num) % self.max_num,
          code='too_many_forms',
        )
      if (self.validate_min and self.total_form_count() - len(self.deleted_forms) - empty_forms_count < self.min_num):
        raise ValidationError(ngettext(
          "Please submit %d or more forms.",
          "Please submit %d or more forms.", self.min_num) % self.min_num,
          code='too_few_forms')
      # Give self.clean() a chance to do cross-form validation.
      self.clean()
    except ValidationError as e:
        self._non_form_errors = self.error_class(e.error_list)

class CladeGroupForm(forms.Form):
  clade_group = forms.CharField(widget = forms.SelectMultiple({'class': 'form-control multiselect clade-group-select'}), required = False)

class BaseCladeGroupFormSet(DummyFormSet):
  def __init__(self, *args, **kwargs):
    super().__init__(0, *args, **kwargs)

  def get_clade_groups(self):
    clade_groups = []
    for i, form in enumerate(self.forms):
      if i == 0: continue # skip first dummy row
      clade_group = form['clade_group'].value()
      if clade_group is not None and len(clade_group) > 0:
        clade_groups.append(clade_group)
    return clade_groups

  def get_clade_group_names(self):
    clade_group_names = []
    for i, form in enumerate(self.forms):
      if i == 0: continue # skip first dummy row
      names = []
      clade_group = form['clade_group'].value()
      if clade_group is not None and len(clade_group) > 0:
        for clade_taxid, clade in choices.CLADES:
          if clade_taxid in clade_group: 
            names.append(clade)
        clade_group_names.append(names)
    return clade_group_names

  def clean(self):
    if len(self.get_clade_groups()) == 0:
      raise ValidationError('no clades specified')

CladeGroupFormSet = formset_factory(CladeGroupForm, formset = BaseCladeGroupFormSet, extra = 3)

class DistributionForm(forms.Form):
  isotypes = forms.MultipleChoiceField(
    widget = forms.SelectMultiple({'class': 'form-control multiselect isotype-select'}),
    initial = '',
    choices = choices.ISOTYPES,
    required = True)
  positions = forms.MultipleChoiceField(
    widget = forms.SelectMultiple({'class': 'form-control multiselect position-select'}),
    initial = '',
    choices = choices.POSITIONS,
    required = True)

class FocusForm(forms.Form):
  position = forms.ChoiceField(
    widget = forms.Select({'class': 'form-control multiselect position-select'}),
    choices = choices.POSITIONS_DISTINCT,
    required = True)
  isotype = forms.ChoiceField(
    widget = forms.Select({'class': 'form-control multiselect isotype-select'}), 
    initial = 'All',
    choices = choices.ISOTYPES,
    required = True)
  anticodon = forms.ChoiceField(
    widget = forms.Select({'class': 'form-control multiselect anticodon-select'}), 
    initial = 'All',
    choices = choices.ANTICODONS,
    required = True)
  score = forms.CharField(
    initial = '{} - {}'.format(models.tRNA.objects.aggregate(Min('score'))['score__min'], models.tRNA.objects.aggregate(Max('score'))['score__max'],
    required = True)
  )

  def as_dict(self):
    score_min, score_max = self['score'].value().split(' - ')
    return {
      'position': str(self['position'].value()),
      'isotype': str(self['isotype'].value()),
      'anticodon': str(self['anticodon'].value()),
      'score_min': score_min,
      'score_max': score_max
    }

class BaseFocusFormSet(DummyFormSet):
  def __init__(self, *args, **kwargs):
    super().__init__(0, *args, **kwargs)
    for form in self.forms:
      form.empty_permitted = False

  def get_foci(self):
    foci = []
    for i, form in enumerate(self.forms):
      if i == 0: continue # skip first dummy row
      focus = form.as_dict()
      if focus['position'] == '' or focus['isotype'] == '' or focus['anticodon'] == '':
        continue
      foci.append(focus)
    return foci

  def clean(self):
    if len(self.get_foci()) == 0:
      raise ValidationError('no foci specified')

FocusFormSet = formset_factory(FocusForm, formset = BaseFocusFormSet, extra = 3)

class CompareForm(forms.Form):
  name = forms.CharField(
    widget = forms.TextInput({'class': 'form-control name-input', 'placeholder': 'Fill in your selection label'}), 
    max_length = 20, 
    required = False)
  fasta = forms.CharField(
    widget = forms.Textarea({
      'class': 'form-control fasta-input',
      'placeholder': 'Paste tRNAs in FASTA format'
    }), 
    required = False)
  clade = forms.ChoiceField(choices = choices.CLADES, required = False)
  isotype = forms.ChoiceField(
    widget = forms.Select({'class': 'form-control multiselect isotype-select'}), 
    initial = 'All',
    choices = choices.ISOTYPES,
    required = False)
  use_fasta = forms.ChoiceField(
    widget = forms.RadioSelect(),
    choices = (('False', 'Select tRNAs'), ('True', 'Input FASTA')),
    initial = 'False',
    required = True)
  domain = forms.ChoiceField(
    widget = forms.RadioSelect(),
    choices = choices.NUM_MODELS, 
    initial = 'Universal', 
    required = False)

  def as_dict(self):
    return {
      'name': str(self['name'].value()),
      'fasta': str(self['fasta'].value()),
      'clade': str(self['clade'].value()),
      'isotype': str(self['isotype'].value()),
      'use_fasta': str(self['use_fasta'].value()),
      'domain': str(self['domain'].value())
    }

  def _clean_fields(self):
    # validate fields, but only validate fasta sequence if necessary
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

    if self.cleaned_data['use_fasta'] == "True":
      try:
        # perform regular validation first
        self.cleaned_data['fasta'] = self.fields['fasta'].clean(fasta)
        self.check_fasta(self.cleaned_data['fasta'])
      except ValidationError as e:
        self.add_error('fasta', e)
    else:
      self.cleaned_data['fasta'] = fasta
      # Do a final validation to make sure clade / isotype aren't empty values
      if 'clade' in self.cleaned_data and self.cleaned_data['clade'] == '':
        self.add_error('clade', 'Please make a selection for both clade and isotype fields')
      if 'isotype' in self.cleaned_data and self.cleaned_data['isotype'] == '':
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

class BaseCompareFormSet(DummyFormSet):
  def __init__(self, *args, **kwargs):
    super().__init__(1, *args, **kwargs)
    for form in self.forms:
      form.empty_permitted = False

  def get_compare_list(self):
    compare_list = []
    for i, form in enumerate(self.forms):
      if i == 1: continue # skip first dummy row
      compare = form.as_dict()
      if compare['isotype'] == '' and compare['fasta'] == '':
        continue
      compare_list.append(compare)
    return compare_list
                                                                                            
  def clean(self):
    ref_form = self.forms[0]
    if ref_form.is_valid():
      trna_qs = compare.query_trnas(ref_form.cleaned_data)
      if len(trna_qs) < 5:
        raise ValidationError('Not enough sequences in database for reference category. Query a broader set.')
  
CompareFormSet = formset_factory(CompareForm, formset = BaseCompareFormSet, can_delete = True, extra = 3)
