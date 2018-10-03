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


@tag('variation', 'distribution')
class DistributionFormTests(TestCase):
  def setUp(self):
    self.clade_groups = [['4930', '4895'], ['5204']]
    self.clade_group_names = [['Saccharomyces (genus)', 'Schizosaccharomyces (genus)'], ['Basidiomycota (phylum)']]
    self.form_data = {
      'clade_group_1': self.clade_groups[0], 
      'clade_group_2': self.clade_groups[1],
      'isotypes': ['Arg', 'Glu', 'His'],
      'positions': ['8', '9', '14', '35', '36', '37', '46', '73', '12:23', '18:55', '11:24']
    }
    self.invalid_form_data = {
      'clade_group_1': ['0', 'invalid'],
      'isotypes': ['not an isotype', 'also not an isotype'],
      'positions': ['p8', 'p9', 'p24']
    }
    self.empty_clade_form_data = {
      'isotypes': ['Arg', 'Glu', 'His'],
      'positions': ['8', '9', '14', '35', '36', '37', '46', '73', '12:23', '18:55', '11:24']
    }

  @tag('species')
  def test_get_clade_groups(self):
    form = forms.DistributionForm(self.form_data)
    clade_groups = form.get_clade_groups()
    self.assertEqual(clade_groups, self.clade_groups)

  @tag('species')
  def test_get_clade_group_names(self):
    form = forms.DistributionForm(self.form_data)
    clade_group_names = form.get_clade_group_names()
    self.assertEqual(clade_group_names, self.clade_group_names)

  @tag('species')
  def test_clade_group_form_clean_raises_error(self):
    form = forms.DistributionForm(self.empty_clade_form_data)
    with self.assertRaisesMessage(ValidationError, 'no clades specified'):
      form.clean()

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
class SpeciesFormTests(TestCase):
  def setUp(self):
    self.clade_groups = [['4930', '4895'], ['5204']]
    self.form_data = {
      'clade_group_1': self.clade_groups[0], 
      'clade_group_2': self.clade_groups[1],
      'focus_1_0': 'Asn',
      'focus_1_1': '46',
      'focus_2_0': 'Met',
      'focus_2_1': '46'
    }
    self.foci = [('Asn', '46'), ('Met', '46')]

    self.invalid_form_data = {
      'clade_group_1': ['0', 'invalid'],
      'focus_1_0': 'n/a',
      'focus_1_1': 'n/a'
    }
    self.invalid_focus_form_data = {
      'clade_group_1': self.clade_groups[0], 
      'clade_group_2': self.clade_groups[1],
      'focus_1_0': 'Met',
      'focus_1_1': '',
    }
    self.empty_focus_form_data = {
      'clade_group_1': self.clade_groups[0], 
      'clade_group_2': self.clade_groups[1],
      'focus_1_0': '',
      'focus_1_1': '',
    }

  def test_species_form_valid_clade_select(self):
    clade_group_form = forms.SpeciesCladeForm(data = self.form_data)
    self.assertTrue(clade_group_form.is_valid())

  @tag('current')
  def test_species_form_valid_foci_select(self):
    focus_form = forms.FocusFormSet(data = self.form_data)
    import pdb
    pdb.set_trace()
    self.assertTrue(focus_form.is_valid())

  def test_species_form_invalid_select(self):
    form = forms.SpeciesDistributionForm(data = self.invalid_form_data)
    self.assertFalse(form.is_valid())

  def test_species_form_malformed_form(self):
    form = forms.SpeciesDistributionForm(data = {'invalid': 'void'})
    self.assertFalse(form.is_valid())

  def test_focus_form_clean_raises_error(self):
    form = forms.SpeciesDistributionForm(self.empty_focus_form_data)
    with self.assertRaisesMessage(ValidationError, 'no foci specified'):
      form.clean()
    self.assertFalse(form.is_valid())

    # self.assertIn('did not select an isotype/position pair', form.errors['focus_1'])

  def test_get_foci(self):
    form = forms.SpeciesDistributionForm(self.form_data)
    self.assertTrue(form.is_valid())
    foci = form.get_foci()
    self.assertEqual(foci, self.foci)


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
    self.assertEqual(form.errors['isotype'][0], 'Select a valid choice. isotype is not one of the available choices.')

  def test_compare_form_valid_fasta(self):
    form_data = {'name': 'test-name', 'fasta': '>myseq\nACTG', 'clade': '4930', 'isotype': 'All', 'use_fasta': True}
    form = forms.CompareForm(data = form_data)
    self.assertTrue(form.is_valid())

  def test_compare_form_empty_fasta(self):
    form_data = {'name': 'test-name', 'fasta': '', 'clade': '4930', 'isotype': 'All', 'use_fasta': True}
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())

  def test_compare_form_malformed_fasta(self):
    form_data = {'name': 'test-name', 'fasta': 'AGACAGCGATGC', 'clade': '4930', 'isotype': 'All', 'use_fasta': True}
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())

    form_data['fasta'] = 'ACTGACATCGTAGCTAGTACG'
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())
    
  def test_compare_form_bad_chars_fasta(self):
    form_data = {'name': 'test-name', 'fasta': '12345', 'clade': '4930', 'isotype': 'All', 'use_fasta': True}
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())

    form_data['fasta'] = '>myseq\nACTGACATCGTAGCTAGTACG\n%%%%^^^***AF<><>AJFJGOSFES\nACTATATA\n>seq2\nACACACACACACAC'
    form = forms.CompareForm(data = form_data)
    self.assertFalse(form.is_valid())

  def test_compare_formset_ref_model_insufficient_trnas(self):
     # Amanita (genus) only has 4 Asp tRNAs
    formset = forms.CompareFormSet({
      'form-0-name': '', 'form-0-clade': '41955', 'form-0-isotype': 'Asp',
      'form-1-name': '', 'form-1-clade': '2759', 'form-1-isotype': 'All', 'form-1-domain': 'uni',
      'form-2-name': 'Test', 'form-2-clade': '4893', 'form-2-isotype': 'All', 'form-2-domain': 'euk',
      'form-TOTAL_FORMS': '3', 'form-MIN_NUM_FORMS': '0', 'form-MAX_NUM_FORMS': '1000', 'form-INITIAL_FORMS': '0'
    })
    for form in formset:
      form.is_valid()
    with self.assertRaisesMessage(ValidationError, 'Not enough sequences in database for reference category. Query a broader set.'):
      formset.clean()
  
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


