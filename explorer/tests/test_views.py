from django.test import TestCase, Client, tag
from django.test.client import RequestFactory

from explorer import models
from explorer import views


class SummaryTests(TestCase):
  def setUp(self):
    self.client = Client()
    self.filter_taxid = '4930'
    self.filter_clade = ('Saccharomyces', 'genus')
    self.filter_isotype = 'All'
    self.clade_dict = {'4930': ('Saccharomyces', 'genus')}
    self.isotype_list = ISOTYPES


  def test_summary_redirects(self):
    response = self.client.get('/')
    self.assertEqual(response.status_code, 302)
    response = self.client.get('/summary')
    self.assertEqual(response.status_code, 301)

  def test_summary_get(self):
    response = self.client.get('/summary/')
    self.assertEqual(response.status_code, 200)

  def test_summary_valid_post(self):
    response = self.client.post('/summary/', {
      'clade': self.filter_clade,
      'clade_txid': self.filter_taxid,
      'isotype': self.filter_isotype,
      'clade_dict': self.clade_dict,
      'isotype_list': self.isotype_list})


class CompareViewTests(TestCase):
  def setUp(self):
    self.client = Client()

  def test_compare_get_response(self):
    response = self.client.get('/compare/')
    self.assertEqual(response.status_code, 200)



class VariationViewTests(TestCase):
  def setUp(self):
    self.client = Client()

  def test_variation_distribution_get_response(self):
    response = self.client.get('/variation/distribution')
    self.assertEqual(response.status_code, 200)

  def test_species_distribution_get_response(self):
    response = self.client.get('/variation/species')
    self.assertEqual(response.status_code, 200)

