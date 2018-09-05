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

@tag('api', 'variation')
class VariationServicesTests(TestCase):
  def setUp(self):
    self.factory = RequestFactory()
    self.api_txids = '4930,4895;5204'
    self.api_positions = 'paired,1:72,variable,2:71,8'
    self.api_isotypes = 'His,Met,Phe'
    self.clade_groups = [['4930', '4895'], ['5204']]
    self.num_groups = 2
    self.clade_info = {
      '5204': ('Basidiomycota', 'phylum'), 
      '4895': ('Schizosaccharomyces', 'genus'), 
      '4930': ('Saccharomyces', 'genus')
    }
    self.positions = ['1:72', '2:71', '3:70', '4:69', '5:68', '6:67', '7:66', '8', '10:25', '11:24', '12:23', '13:22', '27:43', '28:42', '29:41', '30:40', '31:39', 'V1', 'V2', 'V3', 'V4', 'V5', 'V11:V21', 'V12:V22', 'V13:V23', 'V14:V24', 'V15:V25', 'V16:V26', 'V17:V27', '49:65', '50:64', '51:63', '52:62', '53:61']
    self.query_positions = ['p1_72', 'p2_71', 'p3_70', 'p4_69', 'p5_68', 'p6_67', 'p7_66', 'p8', 'p10_25', 'p11_24', 'p12_23', 'p13_22', 'p27_43', 'p28_42', 'p29_41', 'p30_40', 'p31_39', 'pV1', 'pV2', 'pV3', 'pV4', 'pV5', 'pV11_V21', 'pV12_V22', 'pV13_V23', 'pV14_V24', 'pV15_V25', 'pV16_V26', 'pV17_V27', 'p49_65', 'p50_64', 'p51_63', 'p52_62', 'p53_61']
    self.query_positions.append('isotype')
    self.isotypes = ['His', 'Met', 'Phe']
    self.trnas = services.query_trnas_for_distribution(self.clade_groups, self.clade_info, self.isotypes, self.query_positions)
    self.freqs = services.convert_trnas_to_freqs_df(self.trnas)
    self.plot_data = services.convert_freqs_to_dict(self.freqs)

  @tag('distribution')
  def test_services_reconstruct_clade_group_info(self):
    clade_groups, clade_info = services.reconstruct_clade_group_info(self.api_txids)
    self.assertEqual(len(clade_groups), 2)
    self.assertEqual(len(clade_info), 3)
    self.assertEqual(clade_info['5204'], ('Basidiomycota', 'phylum'))

  @tag('distribution')
  def test_services_uniquify_positions(self):
    positions = services.uniquify_positions('8,9')
    self.assertEqual(positions, ['8', '9'])
    positions = services.uniquify_positions(self.api_positions)
    self.assertEqual(positions, self.positions)
  

  @tag('distribution')
  def test_services_query_trnas_for_distribution(self):
    self.assertEqual(len(self.trnas.columns), 36)
    self.assertIn('group', self.trnas.columns)
    self.assertIn('isotype', self.trnas.columns)

  @tag('distribution')
  def test_services_convert_trnas_to_freqs_df(self):
    self.assertIn('isotype', self.freqs.columns)
    self.assertIn('group', self.freqs.columns)
    self.assertIn('position', self.freqs.columns)
    self.assertEqual(len(self.freqs.index.levels), 3)
    self.assertEqual(set(self.isotypes), set(self.freqs.index.levels[0]))
    self.assertEqual(set(self.positions), set(self.freqs.index.levels[1]))

  @tag('distribution')
  def test_services_convert_freqs_to_dict(self):
    self.assertEqual(len(self.plot_data), len(self.isotypes))
    for isotype in self.isotypes:
      with self.subTest(isotype = isotype):
        self.assertEqual(len(self.plot_data[isotype]), len(self.positions))
        for position in self.positions:
          with self.subTest(position = position):
            self.assertEqual(len(self.plot_data[isotype][position]), self.num_groups)

  @tag('distribution')
  def test_services_distribution(self):
    request = self.factory.post('/api/distribution')
    json_response = services.distribution(request, self.api_txids, self.api_isotypes, self.api_positions)
    plot_data = json.loads(json_response.content.decode('utf8'))
    self.assertEqual(type(plot_data), dict)
    self.assertTrue(len(plot_data) > 0)
