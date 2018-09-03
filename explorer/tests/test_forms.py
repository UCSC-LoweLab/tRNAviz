from django.test import TestCase, Client, tag
from django.test.client import RequestFactory

from explorer import models
from explorer import choices
from explorer.forms import *
from explorer.views import ISOTYPES

class SummaryFormTests(TestCase):
  def setUp(self):
    self.client = Client()
    self.filter_taxid = '4930'
    self.filter_clade = ('Saccharomyces', 'genus')
    self.filter_isotype = 'All'
    self.clade_dict = {'4930': ('Saccharomyces', 'genus')}
    self.isotype_list = ISOTYPES

  def test_summary_form_clade_choices(self):
    pass


class CompareFormTests(TestCase):
  def test_compare_form_valid_select(self):
    form_data = {'name': 'test-name', 'fasta': '', 'clade': '4930', 'isotype': 'All', 'use_fasta': False}
    form = CompareForm(data = form_data)
    self.assertTrue(form.is_valid())

  def test_compare_form_invalid_clade_select(self):
    form_data = {'name': 'test-name', 'fasta': '', 'clade': 'asdf', 'isotype': 'All', 'use_fasta': False}
    form = CompareForm(data = form_data)
    self.assertFalse(form.is_valid())
    self.assertEquals(form.errors['clade'][0], 'Select a valid choice. asdf is not one of the available choices.')

  def test_compare_form_invalid_isotype_select(self):
    form_data = {'name': 'test-name', 'fasta': '', 'clade': '4930', 'isotype': 'isotype', 'use_fasta': False}
    form = CompareForm(data = form_data)
    self.assertFalse(form.is_valid())
    self.assertEquals(form.errors['isotype'][0], 'Select a valid choice. isotype is not one of the available choices.')

  @tag('not-done')
  def test_compare_form_valid_fasta(self):
    form_data = {'name': 'test-name', 'fasta': '>myseq\nACTG', 'clade': '4930', 'isotype': 'All', 'use_fasta': True}
    form = CompareForm(data = form_data)
    self.assertTrue(form.is_valid())

  @tag('not-done')
  def test_compare_form_empty_fasta(self):
    form_data = {'name': 'test-name', 'fasta': '', 'clade': '4930', 'isotype': 'All', 'use_fasta': True}
    form = CompareForm(data = form_data)
    self.assertFalse(form.is_valid())

  @tag('not-done')
  def test_compare_form_malformed_fasta(self):
    form_data = {'name': 'test-name', 'fasta': 'AGACAGCGATGC', 'clade': '4930', 'isotype': 'All', 'use_fasta': True}
    form = CompareForm(data = form_data)
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
    form = CompareForm(data = form_data)
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
    form = CompareForm(data = form_data)
    self.assertTrue(form.is_valid())
    self.assertFalse(form.has_error('clade'))
    self.assertFalse(form.has_error('isotype'))
    



