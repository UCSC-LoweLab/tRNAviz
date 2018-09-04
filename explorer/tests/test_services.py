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
    self.cloverleaf_cons = models.Consensus.objects.filter(taxid = self.clade_txid, isotype = self.isotype).values()[0]
    self.cloverleaf_freqs = services.gather_cloverleaf_freqs(self.clade_txid, self.isotype)
    self.tilemap_cons = models.Consensus.objects.filter(taxid = self.clade_txid).exclude(isotype = 'All').values()
    self.tilemap_freqs = services.gather_tilemap_freqs(clade_txid = self.clade_txid)

  @tag('compare', 'cloverleaf')
  def test_services_coords(self):
    response = self.client.get('/api/coords')
    coords_list = json.loads(response.content.decode('utf8'))
    self.assertEqual(len(coords_list), 95)
    for key in ['x', 'y', 'position', 'radius']:
      with self.subTest(key = key):
        self.assertIn(key, coords_list[0].keys())

  @tag('cloverleaf')
  def test_services_gather_cloverleaf_freqs(self):
    freqs = services.gather_cloverleaf_freqs(self.clade_txid, self.isotype)
    num_positions = len(freqs)
    self.assertEqual(num_positions, 67)
    self.assertEqual(len(freqs['17a']), 5)
    for feature in services.SUMMARY_SINGLE_FEATURES:
      with self.subTest(feature = feature):
        self.assertIn(feature, freqs['17a'])
    self.assertEqual(len(freqs['3:70']), 25)
    for feature in services.SUMMARY_PAIRED_FEATURES.values():
      with self.subTest(feature = feature):
        self.assertIn(feature, freqs['3:70'])
    
  @tag('cloverleaf')
  def test_services_annotate_cloverleaf_positions(self):
    plot_data = services.annotate_cloverleaf_positions(self.cloverleaf_cons, self.cloverleaf_freqs)
    self.assertEqual(len(plot_data), 95)
    for position in plot_data:
      with self.subTest(position = position):
        self.assertIn('freqs', plot_data[position])
        self.assertIn('consensus', plot_data[position])
  
  @tag('cloverleaf')
  def test_services_cloverleaf(self):
    request = self.factory.post('/api/cloverleaf')
    json_response = services.cloverleaf(request, self.clade_txid, self.isotype)
    plot_data = json.loads(json_response.content.decode('utf8'))
    self.assertEqual(len(plot_data), 95)

  @tag('tilemap')
  def test_services_tilemap_gather_freqs(self):
    freqs = services.gather_tilemap_freqs(self.clade_txid)
    for isotype in freqs:
      isotype_freqs = freqs[isotype]
      with self.subTest(isotype = isotype):
        self.assertEqual(len(isotype_freqs), 67)
        self.assertEqual(len(isotype_freqs['17a']), 5)
        self.assertEqual(len(isotype_freqs['3:70']), 25)

  @tag('tilemap')
  def test_services_annotate_tiles(self):
    plot_data = services.annotate_tiles(self.tilemap_cons, self.tilemap_freqs)
    for tile_data in plot_data:
      for key in ['isotype', 'type', 'consensus', 'position', 'freqs']:
        with self.subTest(key = key):
          self.assertIn(key, tile_data)
          if key != 'freqs':
            self.assertEqual(type(tile_data[key]), str)

  @tag('tilemap')
  def test_services_tilemap(self):
    request = self.factory.post('/api/tilemap')
    json_response = services.tilemap(request, self.clade_txid)
    plot_data = json.loads(json_response.content.decode('utf8'))
    self.assertEqual(len(plot_data), 1995) # 21 isotypes * 95 positions
