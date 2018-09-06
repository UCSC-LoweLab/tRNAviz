from django.test import TestCase, Client, tag
from django.test import RequestFactory
from django.urls import reverse

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
    self.assertContains(response, '<td>{}</td>'.format(self.default_clade))
    self.assertContains(response, '<td>{}</td>'.format(self.default_isotype))

  def test_summary_view_valid_post(self):
    request = self.factory.post(reverse('explorer:summary'), {
      'clade': self.clade_txid,
      'isotype': self.isotype
    })
    response = views.summary(request)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, '<td>{}</td>'.format(self.clade))
    self.assertContains(response, '<td>{}</td>'.format(self.isotype))
  
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
      'clade_group_1': self.clade_txids[0],
      'clade_group_2': self.clade_txids[1],
      'clade_group_3': self.clade_txids[2],
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
      'clade_group_1': self.clade_txids[0],
      'clade_group_2': self.clade_txids[1],
      'clade_group_3': self.clade_txids[2],
      'focus_1_0': ['Asn'],
      'focus_1_1': ['8']
    }

  def test_species_view_get(self):
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, '<td><p>Group 1: Schizosaccharomyces (genus)')
    self.assertContains(response, 'Group 2: Saccharomyces (genus)</p></td>')
    self.assertContains(response, '<td><p>Ala, 3:70<br>Gly, 3:70<br>Ala, 46<br>Gly, 46</p></td>')

  @tag('current')
  def test_species_view_post(self):
    request = self.factory.post(reverse('explorer:variation_species'), self.valid_post_data)
    import pdb
    pdb.set_trace()
    response = views.variation_species(request)