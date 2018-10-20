from django.test import TestCase, Client, tag
from django.test import RequestFactory
from django.urls import reverse
from django.core.exceptions import ValidationError

from explorer import views

@tag('summary')
class SummaryViewTests(TestCase):
  def setUp(self):
    self.factory = RequestFactory()
    self.clade_txid = '5204'
    self.default_clade = 'Saccharomyces (genus)'
    self.default_isotype = 'All'
    self.clade = 'Basidiomycota (phylum)'
    self.isotype = 'Asn'

  def test_summary_view_get(self):
    request = self.factory.get(reverse('explorer:summary'))
    response = views.summary(request)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, '{}'.format(self.default_clade))
    self.assertContains(response, '{}'.format(self.default_isotype))
  
  def test_summary_view_valid_post(self):
    request = self.factory.post(reverse('explorer:summary'), {
      'clade': self.clade_txid,
      'isotype': self.isotype
    })
    response = views.summary(request)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, '{}'.format(self.clade))
    self.assertContains(response, '{}'.format(self.isotype))
  
  def test_summary_view_invalid_post(self):
    request = self.factory.post(reverse('explorer:summary'), {
      'clade': 'invalid',
      'isotype': 'void'
    })
    response = views.summary(request)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Error in clade')
    self.assertContains(response, 'Error in isotype')
    self.assertContains(response, '<td>{}</td>'.format(self.default_clade))
    self.assertContains(response, '<td>{}</td>'.format(self.default_isotype))

@tag('variation', 'distribution')
class DistributionViewTests(TestCase):
  def setUp(self):
    self.factory = RequestFactory()
    self.clade_txids = [['4930'], ['5204'], ['6033']]
    self.positions = ['paired', '1:72', 'variable' ,'2:71', '8']
    self.isotypes = ['His', 'Met', 'Phe']

  def test_distribution_view_get(self):
    request = self.factory.get(reverse('explorer:variation_distribution'))
    response = views.variation_distribution(request)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, '<td><p>Group 1: Saccharomyces (genus), Schizosaccharomyces (genus)')
    self.assertContains(response, 'Group 2: Basidiomycota (phylum)</p></td>')
    self.assertContains(response, '<td>All</td>')
    self.assertContains(response, '<td>8, 9, 14, 35, 36, 37, 46, 73, 12:23, 18:55, 11:24</td>')

  @tag('distribution')
  def test_distribution_view_valid_post(self):
    request = self.factory.post(reverse('explorer:variation_distribution'), {
      'clade-0-clade_group': '',
      'clade-1-clade_group': self.clade_txids[0],
      'clade-2-clade_group': self.clade_txids[1],
      'clade-3-clade_group': self.clade_txids[2],
      'clade-TOTAL_FORMS': '4', 'clade-MIN_NUM_FORMS': '0', 'clade-MAX_NUM_FORMS': '1000', 'clade-INITIAL_FORMS': '0',
      'isotypes': self.isotypes,
      'positions': self.positions
    })
    response = views.variation_distribution(request)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Group 1: Saccharomyces (genus)')
    self.assertContains(response, 'Group 2: Basidiomycota (phylum)')
    self.assertContains(response, 'Group 3: Encephalitozoon (genus)')
    self.assertContains(response, 'paired, 1:72, variable, 2:71, 8')
    self.assertContains(response, 'His, Met, Phe')


@tag('variation', 'species')
class SpeciesViewTests(TestCase):
  def setUp(self):
    self.factory = RequestFactory()
    self.clade_txids = [['4930'], ['5204'], ['6033']]
    self.valid_post_data = {
      'clade-0-clade_group': '',
      'clade-1-clade_group': self.clade_txids[0],
      'clade-2-clade_group': self.clade_txids[1],
      'clade-3-clade_group': self.clade_txids[2],
      'clade-TOTAL_FORMS': '4', 'clade-MIN_NUM_FORMS': '0', 'clade-MAX_NUM_FORMS': '1000', 'clade-INITIAL_FORMS': '0',
      'focus-0-isotype': 'All', 'focus-0-position': '', 'focus-0-anticodon': 'All', 'focus-0-score': '16.5 - 109.5',
      'focus-1-isotype': 'Gly', 'focus-1-position': '3:70', 'focus-1-anticodon': 'All', 'focus-1-score': '16.5 - 109.5',
      'focus-2-isotype': 'Met', 'focus-2-position': '3:70', 'focus-2-anticodon': 'All', 'focus-2-score': '30.5 - 80',
      'focus-TOTAL_FORMS': '3', 'focus-MIN_NUM_FORMS': '0', 'focus-MAX_NUM_FORMS': '1000', 'focus-INITIAL_FORMS': '0'
    
    }

  def test_species_view_get(self):
    request = self.factory.get(reverse('explorer:variation_species'))
    response = views.variation_species(request)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Group 1: Saccharomyces (genus), Schizosaccharomyces (genus)')
    self.assertContains(response, '<td>3:70</td>')
    self.assertContains(response, '<td>Gly</td>')
    self.assertContains(response, '<td>All</td>')
    self.assertContains(response, '<td>16.5 - 100.1</td>')
    self.assertContains(response, '<td>16.5 - 70.1</td>')

  def test_species_view_valid_post(self):
    request = self.factory.post(reverse('explorer:variation_species'), self.valid_post_data)
    response = views.variation_species(request)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'Group 1: Saccharomyces (genus)')
    self.assertContains(response, 'Group 2: Basidiomycota (phylum)')
    self.assertContains(response, 'Group 3: Encephalitozoon (genus)')
    self.assertContains(response, '<td>Met</td>')
    self.assertContains(response, '<td>30.5 - 80</td>')

@tag('compare')
class CompareViewTests(TestCase):
  def setUp(self):
    self.factory = RequestFactory()
    self.valid_post_data = {
      'form-0-name': '',
      'form-0-clade': '4893',
      'form-0-isotype': 'All',
      'form-1-name': '',
      'form-1-clade': '',
      'form-1-isotype': '',
      'form-2-clade': '2759',
      'form-2-name': 'Test',
      'form-2-isotype': 'All',
      'form-TOTAL_FORMS': '3',
      'form-MIN_NUM_FORMS': '0',
      'form-MAX_NUM_FORMS': '1000',
      'form-INITIAL_FORMS': '0'
    }
    self.invalid_post_data = {'form': 'invalid'}
    self.invalid_form_data = {
      'form-0-name': '', 'form-0-clade': '41955', 'form-0-isotype': 'Asp',
      'form-1-name': '', 'form-1-clade': '2759', 'form-1-isotype': 'All', 'form-1-domain': 'uni',
      'form-2-name': 'Test', 'form-2-clade': '4893', 'form-2-isotype': 'All', 'form-2-domain': 'euk',
      'form-TOTAL_FORMS': '3', 'form-MIN_NUM_FORMS': '0', 'form-MAX_NUM_FORMS': '1000', 'form-INITIAL_FORMS': '0'
    }

  def test_compare_view_get(self):
    request = self.factory.get(reverse('explorer:compare'))
    response = views.compare(request)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, '<h4>Selections</h4>')

  def test_compare_view_get_no_errors(self):
    request = self.factory.get(reverse('explorer:compare'))
    response = views.compare(request)
    self.assertNotContains(response, 'The following errors were found:')

  def test_compare_view_valid_post(self):
    request = self.factory.post(reverse('explorer:compare'), self.valid_post_data)
    response = views.compare(request)
    self.assertEqual(response.status_code, 200)

  def test_compare_view_invalid_post_raises_error(self):
    request = self.factory.post(reverse('explorer:compare'), self.invalid_post_data)
    with self.assertRaises(ValidationError):
      response = views.compare(request)
  
  def test_compare_view_form_errors_rendered(self):
    request = self.factory.post(reverse('explorer:compare'), self.invalid_form_data)
    response = views.compare(request)
    self.assertContains(response, 'The following errors were found:')
    self.assertContains(response, 'Not enough sequences in database for reference')


class TaxonomyServicesTests(TestCase):
  def setUp(self):
    self.factory = RequestFactory() 

  @tag('current')
  def test_taxonomy_get(self):
    request = self.factory.get(reverse('explorer:taxonomy'))
    response = views.taxonomy(request)
    self.assertEqual(response.status_code, 200)