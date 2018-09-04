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
