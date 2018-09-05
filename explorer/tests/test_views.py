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

@tag('variation')
class VariationViewTests(TestCase):
  def setUp(self):
    self.factory = RequestFactory()

  @tag('distribution')
  def test_distribution_view_get(self):
    request = self.factory.get(reverse('explorer:variation_distribution'))
    response = views.variation_distribution(request)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, '<td><p>Group 1: Saccharomyces (genus), Schizosaccharomyces (genus)')
    self.assertContains(response, 'Group 2: Basidiomycota (phylum)</p></td>')
    self.assertContains(response, '<td>All</td>')
    self.assertContains(response, '<td>8, 9, 14, 35, 36, 37, 46, 73, 12:23, 18:55, 11:24</td>')

  def test_species_view_get(self):
    request = self.factory.get(reverse('explorer:variation_species'))
    response = views.variation_distribution(request)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, '<td><p>Group 1: Schizosaccharomyces (genus)<br>Group 2: Saccharomyces (genus)</p></td>')
    self.assertContains(response, '<td><p>Ala, 3:70<br>Gly, 3:70<br>Ala, 46<br>Gly, 46</p></td>')

  # def test_distribution_view_valid_post(self):
  #   request = self.factory.post(reverse('explorer:variation_distribution'), {'form_clades_1': [{'4930': ('Saccharomyces', 'genus')}]})