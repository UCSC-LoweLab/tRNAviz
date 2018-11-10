from django.test import TestCase, Client, tag
from django.test.client import RequestFactory

from explorer import models
from explorer import choices
from explorer import forms
from explorer import views

from django.core.exceptions import ValidationError

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

@tag('variation')
class CladeGroupFormSetTests(TestCase):
  def setUp(self):
    self.clade_groups = [['4930', '4895'], ['5204']]
    self.clade_group_names = [['Saccharomyces (genus)', 'Schizosaccharomyces (genus)'], ['Basidiomycota (phylum)']]
    self.form_data = {
      'clade-0-clade_group': [],
      'clade-1-clade_group': ['4930', '4895'],
      'clade-2-clade_group': ['5204'],
      'clade-TOTAL_FORMS': '3', 'clade-MIN_NUM_FORMS': '0', 'clade-MAX_NUM_FORMS': '1000', 'clade-INITIAL_FORMS': '0',
    }
    self.empty_clade_form_data = {
      'isotypes': ['Arg', 'Glu', 'His'],
      'positions': ['8', '9', '14', '35', '36', '37', '46', '73', '12:23', '18:55', '11:24'],
      'clade-TOTAL_FORMS': '3', 'clade-MIN_NUM_FORMS': '0', 'clade-MAX_NUM_FORMS': '1000', 'clade-INITIAL_FORMS': '0',
    }

  def test_get_clade_groups(self):
    formset = forms.CladeGroupFormSet(self.form_data, prefix = 'clade')
    clade_groups = formset.get_clade_groups()
    self.assertEqual(clade_groups, self.clade_groups)
    self.assertEqual(len(clade_groups), 2)

  def test_get_clade_group_names(self):
    formset = forms.CladeGroupFormSet(self.form_data, prefix = 'clade')
    clade_group_names = formset.get_clade_group_names()
    self.assertEqual(clade_group_names, self.clade_group_names)
    self.assertEqual(len(clade_group_names), 2)

  def test_clade_group_form_clean_raises_error(self):
    formset = forms.CladeGroupFormSet(self.empty_clade_form_data, prefix = 'clade')
    with self.assertRaisesMessage(ValidationError, 'no clades specified'):
      formset.clean()

@tag('variation', 'distribution')
class DistributionFormTests(TestCase):
  def setUp(self):
    self.form_data = {
      'isotypes': ['Arg', 'Glu', 'His'],
      'positions': ['8', '9', '14', '35', '36', '37', '46', '73', '12:23', '18:55', '11:24']
    }
    self.invalid_form_data = {
      'isotypes': ['not an isotype', 'also not an isotype'],
      'positions': ['p8', 'p9', 'p24']
    }

  def test_distribution_form_valid_select(self):
    form = forms.DistributionForm(data = self.form_data)
    self.assertTrue(form.is_valid())

  def test_distribution_form_invalid_select(self):
    form = forms.DistributionForm(data = self.invalid_form_data)
    self.assertFalse(form.is_valid())
    form = forms.DistributionForm(data = {'invalid': 'void'})
    self.assertFalse(form.is_valid())

@tag('variation', 'species')
class FocusFormSetTests(TestCase):
  def setUp(self):
    self.foci = [{'position': '3:70', 'isotype': 'Gly', 'anticodon': 'All', 'score_max': '109.5', 'score_min': '16.5'}, 
      {'position': '3:70', 'isotype': 'Asn', 'anticodon': 'All', 'score_max': '60.1', 'score_min': '16.5'}]
    self.form_data = {
      'focus-0-isotype': 'Gly', 'focus-0-position': '3:70', 'focus-0-anticodon': 'All', 'focus-0-score': '16.5 - 109.5',
      'focus-1-isotype': 'Gly', 'focus-1-position': '3:70', 'focus-1-anticodon': 'All', 'focus-1-score': '16.5 - 109.5',
      'focus-2-isotype': 'Asn', 'focus-2-position': '3:70', 'focus-2-anticodon': 'All', 'focus-2-score': '16.5 - 60.1',
      'focus-TOTAL_FORMS': '3', 'focus-MIN_NUM_FORMS': '0', 'focus-MAX_NUM_FORMS': '1000', 'focus-INITIAL_FORMS': '0'
    }
    self.invalid_form_data = {
      'focus-0-isotype': 'All', 'focus-0-position': '', 'focus-0-anticodon': 'All', 'focus-0-score': '16.5 - 109.5',
      'focus-1-isotype': '', 'focus-1-position': '', 'focus-1-anticodon': 'All', 'focus-1-score': '16.5 - 109.5',
      'focus-TOTAL_FORMS': '2', 'focus-MIN_NUM_FORMS': '0', 'focus-MAX_NUM_FORMS': '1000', 'focus-INITIAL_FORMS': '0'
    }    
    self.empty_form = {
      'focus-0-isotype': '', 'focus-0-position': '', 'focus-0-anticodon': '', 'focus-0-score': '',
      'focus-TOTAL_FORMS': '1', 'focus-MIN_NUM_FORMS': '0', 'focus-MAX_NUM_FORMS': '1000', 'focus-INITIAL_FORMS': '0'
    }

  def test_focus_formset_valid_select(self):
    focus_formset = forms.FocusFormSet(data = self.form_data, prefix = 'focus')
    self.assertTrue(focus_formset.is_valid())
  
  def test_focus_formset_invalid_form(self):
    focus_formset = forms.FocusFormSet(data = self.invalid_form_data, prefix = 'focus')
    self.assertFalse(focus_formset.is_valid())

  def test_focus_formset_clean_raises_error(self):
    formset = forms.FocusFormSet(self.empty_form, prefix = 'focus')
    with self.assertRaisesMessage(ValidationError, 'no foci specified'):
      formset.clean()
    self.assertFalse(formset.is_valid())

  def test_get_foci(self):
    formset = forms.FocusFormSet(self.form_data, prefix = 'focus')
    self.assertTrue(formset.is_valid())
    foci = formset.get_foci()
    self.assertEqual(foci, self.foci)

@tag('compare')
class CompareFormTests(TestCase):
  def test_compare_form_valid_select(self):
    form_data = {'name': 'test-name', 'fasta': '', 'clade': '4930', 'isotype': 'All', 'use_fasta': 'False'}
    form = forms.CompareForm(data = form_data)
    self.assertTrue(form.is_valid())

  def test_compare_form_invalid_clade_select(self):
    form_data = {'name': 'test-name', 'fasta': '', 'clade': 'asdf', 'isotype': 'All', 'use_fasta': 'False'}
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())
    self.assertEquals(form.errors['clade'][0], 'Select a valid choice. asdf is not one of the available choices.')

  def test_compare_form_invalid_isotype_select(self):
    form_data = {'name': 'test-name', 'fasta': '', 'clade': '4930', 'isotype': 'isotype', 'use_fasta': 'False'}
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())
    self.assertEqual(form.errors['isotype'][0], 'Select a valid choice. isotype is not one of the available choices.')

  def test_compare_form_valid_fasta(self):
    form_data = {'name': 'test-name', 'fasta': '>myseq\nACTG', 'clade': '4930', 'isotype': 'All', 'use_fasta': 'True'}
    form = forms.CompareForm(data = form_data)
    self.assertTrue(form.is_valid())

  def test_compare_form_empty_fasta(self):
    form_data = {'name': 'test-name', 'fasta': '', 'clade': '4930', 'domain': 'Universal', 'isotype': 'All', 'use_fasta': 'True'}
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())

  def test_compare_form_malformed_fasta(self):
    form_data = {'name': 'test-name', 'fasta': 'AGACAGCGATGC', 'domain': 'Universal', 'clade': '4930', 'isotype': 'All', 'use_fasta': 'True'}
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())

  def test_compare_form_bad_chars_fasta(self):
    form_data = {'name': 'test-name', 'fasta': '12345', 'domain': 'Universal', 'clade': '4930', 'isotype': 'All', 'use_fasta': 'True'}
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())

    form_data['fasta'] = '>myseq\nACTGACATCGTAGCTAGTACG\n%%%%^^^***AF<><>AJFJGOSFES\nACTATATA\n>seq2\nACACACACACACAC'
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())

  def test_compare_form_no_domain(self):
    form_data = {'name': 'test-name', 'fasta': '', 'clade': '4930', 'isotype': 'All', 'use_fasta': 'True'}
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())

  def test_compare_full_clean_skips_dummy_form_errors(self):
    formset = forms.CompareFormSet({
      'form-0-name': '', 'form-0-clade': '4930', 'form-0-isotype': 'All', 'form-0-use_fasta': 'False',
      'form-1-name': '', 'form-1-clade': '', 'form-1-isotype': 'All', 'form-1-use_fasta': 'False',
      'form-2-name': 'Test', 'form-2-clade': '4893', 'form-2-isotype': 'All', 'form-2-use_fasta': 'False',
      'form-TOTAL_FORMS': '3', 'form-MIN_NUM_FORMS': '0', 'form-MAX_NUM_FORMS': '1000', 'form-INITIAL_FORMS': '0'
    })
    self.assertTrue(formset.is_valid())
    self.assertEqual(formset.errors[1], {})

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

  def test_compare_form_missing_clade(self):
    form_data = {
      'name': 'test-name',
      'clade': '', 
      'isotype': 'All', 
      'use_fasta': False
    }
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())

  def test_compare_form_error_propagates_to_formset(self):
    formset = forms.CompareFormSet({
      'form-0-name': '', 'form-0-clade': '', 'form-0-isotype': 'Asp', 'form-0-use_fasta': 'False',
      'form-1-name': '', 'form-1-clade': '', 'form-1-isotype': 'All', 'form-1-domain': '', 'form-1-use_fasta': 'False',
      'form-2-name': 'Test', 'form-2-clade': '4893', 'form-2-isotype': 'All', 'form-2-domain': 'Eukaryota', 'form-2-use_fasta': 'False',
      'form-TOTAL_FORMS': '3', 'form-MIN_NUM_FORMS': '0', 'form-MAX_NUM_FORMS': '1000', 'form-INITIAL_FORMS': '0'
    })
    self.assertFalse(formset.is_valid())

  def test_compare_formset_ref_model_insufficient_trnas(self):
     # Amanita (genus) only has 4 Asp tRNAs
    formset = forms.CompareFormSet({
      'form-0-name': '', 'form-0-clade': '41955', 'form-0-isotype': 'Asp', 'form-0-use_fasta': 'False',
      'form-1-name': '', 'form-1-clade': '', 'form-1-isotype': 'All', 'form-1-domain': '', 'form-1-use_fasta': 'False',
      'form-2-name': 'Test', 'form-2-clade': '4893', 'form-2-isotype': 'All', 'form-2-domain': 'Eukaryota', 'form-2-use_fasta': 'False',
      'form-TOTAL_FORMS': '3', 'form-MIN_NUM_FORMS': '0', 'form-MAX_NUM_FORMS': '1000', 'form-INITIAL_FORMS': '0'
    })
    # each form invidiually is valid (minus dummy form 1)
    for i, form in enumerate(formset):
      if i == 1: self.assertFalse(form.is_valid())
      else: self.assertTrue(form.is_valid())
    # this classifies as a formset-wide error
    with self.assertRaisesMessage(ValidationError, 'Not enough sequences in database for reference category. Query a broader set.'):
      formset.clean()
