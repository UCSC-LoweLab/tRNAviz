from django.test import TestCase, Client
from django.test.client import RequestFactory
from explorer import models
from explorer.views import *


class SummaryViewTests(TestCase):
  def setUp(self):
    self.client = Client()
    self.filter_taxid = '4930'
    self.filter_clade = ('Saccharomyces', 'genus')
    self.filter_isotype = 'All'

  def test_summary_redirect(self):
    response = self.client.get('/')
    self.assertEqual(response.status_code, 302)
    print(response)



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