from django.test import TestCase, Client, tag
from django.test.client import RequestFactory

from explorer import models
from explorer import choices
from explorer import forms
from explorer import views

@tag('summary')
class SummaryFormTests(TestCase):
  def setUp(self):
    self.client = Client()
    self.filter_taxid = '4930'
    self.filter_clade = ('Saccharomyces', 'genus')
    self.filter_isotype = 'All'
    self.clade_dict = {'4930': ('Saccharomyces', 'genus')}
    self.isotype_list = choices.ISOTYPES

  def test_summary_form_valid_select(self):
    form_data = {'clade': '4930', 'isotype': 'All'}
    form = forms.SummaryForm(data = form_data)
    self.assertTrue(form.is_valid())

  def test_summary_form_invalid_select(self):
    form_data = {'clade': 'clade', 'isotype': 'All'}
    form = forms.SummaryForm(data = form_data)
    self.assertFalse(form.is_valid())
    form_data = {'clade': '4930', 'isotype': 'isotype'}
    form = forms.SummaryForm(data = form_data)
    self.assertFalse(form.is_valid())

  def test_summary_form_malformed_form(self):
    form_data = {'notafield': 120}
    form = forms.SummaryForm(data = form_data)
    self.assertFalse(form.is_valid())


@tag('variation', 'distribution')
class DistributionFormTests(TestCase):
  def setUp(self):
    self.form_data = {
      'clade-group-1': ['4930', '4895'], 
      'clade-group-2': ['5204'],
      'clade-group-3': [],
      'clade-group-4': [],
      'clade-group-5': [],
      'isotypes': ['Arg', 'Glu', 'His'],
      'positions': ['8', '9', '14', '35', '36', '37', '46', '73', '12:23', '18:55', '11:24']
    }
    self.invalid_form_data = {
      'clade-group-1': ['0', 'invalid'], 
      'clade-group-2': [],
      'clade-group-3': [],
      'clade-group-4': [],
      'clade-group-5': [],
      'isotypes': ['not an isotype', 'also not an isotype'],
      'positions': ['p8', 'p9', 'p24']
    }

  def test_distribution_form_valid_select(self):
    form = forms.DistributionForm(data = self.form_data)
    self.assertTrue(form.is_valid())

  def test_distribution_form_invalid_select(self):
    form = forms.DistributionForm(data = self.invalid_form_data)
    self.assertFalse(form.is_valid())

  def test_distribution_form_malformed_form(self):
    form = forms.DistributionForm(data = {'invalid': 'void'})
    self.assertFalse(form.is_valid())

@tag('variation', 'species')
class DistributionFormTests(TestCase):
  def setUp(self):
    pass

  def test_species_form_valid_select(self):
    pass

  def test_species_form_invalid_select(self):
    pass


  def test_species_form_malformed_form(self):
    pass

   







@tag('compare')
class CompareFormTests(TestCase):
  def test_compare_form_valid_select(self):
    form_data = {'name': 'test-name', 'fasta': '', 'clade': '4930', 'isotype': 'All', 'use_fasta': False}
    form = forms.CompareForm(data = form_data)
    self.assertTrue(form.is_valid())

  def test_compare_form_invalid_clade_select(self):
    form_data = {'name': 'test-name', 'fasta': '', 'clade': 'asdf', 'isotype': 'All', 'use_fasta': False}
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())
    self.assertEquals(form.errors['clade'][0], 'Select a valid choice. asdf is not one of the available choices.')

  def test_compare_form_invalid_isotype_select(self):
    form_data = {'name': 'test-name', 'fasta': '', 'clade': '4930', 'isotype': 'isotype', 'use_fasta': False}
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())
    self.assertEquals(form.errors['isotype'][0], 'Select a valid choice. isotype is not one of the available choices.')

  @tag('not-done')
  def test_compare_form_valid_fasta(self):
    form_data = {'name': 'test-name', 'fasta': '>myseq\nACTG', 'clade': '4930', 'isotype': 'All', 'use_fasta': True}
    form = forms.CompareForm(data = form_data)
    self.assertTrue(form.is_valid())

  @tag('not-done')
  def test_compare_form_empty_fasta(self):
    form_data = {'name': 'test-name', 'fasta': '', 'clade': '4930', 'isotype': 'All', 'use_fasta': True}
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())

  @tag('not-done')
  def test_compare_form_malformed_fasta(self):
    form_data = {'name': 'test-name', 'fasta': 'AGACAGCGATGC', 'clade': '4930', 'isotype': 'All', 'use_fasta': True}
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())

  @tag('not-done')
  def test_compare_form_toggle_disable_fasta_validation(self):
    form_data = {
      'name': 'test-name', 
      'fasta': 'invalid fasta', 
      'clade': '4930', 
      'isotype': 'All', 
      'use_fasta': False
    }
    form = forms.CompareForm(data = form_data)
    self.assertTrue(form.is_valid())
    self.assertFalse(form.has_error('fasta'))

  @tag('not-done')
  def test_compare_form_toggle_disable_select_validation(self):
    form_data = {
      'name': 'test-name', 
      'fasta': '>valid fasta\nACTAGCTGACTA',
      'clade': 'invalid',
      'isotype': 'invalid',
      'use_fasta': True
    }
    form = forms.CompareForm(data = form_data)
    self.assertTrue(form.is_valid())
    self.assertFalse(form.has_error('clade'))
    self.assertFalse(form.has_error('isotype'))
    



