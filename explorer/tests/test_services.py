from django.test import TestCase, Client, tag, RequestFactory
import json
from explorer import models
from explorer import services
from explorer import views


@tag('api', 'summary')
class SummaryServicesTests(TestCase):
  def setUp(self):
    self.client = Client()
    self.factory = RequestFactory()
    self.clade_txid = '4930'
    self.isotype = 'All'
    self.cons = models.Consensus.objects.filter(taxid = self.clade_txid, isotype = self.isotype).values()[0]
    self.freqs = services.gather_cloverleaf_freqs(self.clade_txid, self.isotype)

  @tag('compare')
  def test_services_coords(self):
    response = self.client.get('/api/coords')
    coords_list = json.loads(response.content.decode('utf8'))
    self.assertEqual(len(coords_list), 95)
    for key in ['x', 'y', 'position', 'radius']:
      with self.subTest(key = key):
        self.assertIn(key, coords_list[0].keys())

  def test_services_gather_cloverleaf_freqs(self):
    freqs = services.gather_cloverleaf_freqs(self.clade_txid, self.isotype)
    num_positions = len(freqs)
    self.assertEqual(num_positions, 67)
    self.assertEqual(len(freqs['17a']), 5)
    for feature in services.CLOVERLEAF_SINGLE_FEATURES:
      with self.subTest(feature = feature):
        self.assertIn(feature, freqs['17a'])
    self.assertEqual(len(freqs['3:70']), 25)
    for feature in services.CLOVERLEAF_PAIRED_FEATURES.values():
      with self.subTest(feature = feature):
        self.assertIn(feature, freqs['3:70'])
    
  def test_services_annotate_cloverleaf_positions(self):
    plot_data = services.annotate_cloverleaf_positions(self.cons, self.freqs)
    self.assertEqual(len(plot_data), 95)
    for position in plot_data:
      with self.subTest(position = position):
        self.assertIn('freqs', plot_data[position])
        self.assertIn('consensus', plot_data[position])
  
  @tag('current')
  def test_services_cloverleaf(self):
    request = self.factory.post('/api/cloverleaf')
    json_response = services.cloverleaf(request, self.clade_txid, self.isotype)
    plot_data = json.loads(json_response.content.decode('utf8'))
    self.assertEqual(len(plot_data), 95)
