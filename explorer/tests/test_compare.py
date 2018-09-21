from django.test import TestCase, Client, tag, RequestFactory
from django.urls import reverse
from django.conf import settings

import shutil
from tempfile import NamedTemporaryFile, mkdtemp
import json
import pandas as pd
from Bio import SeqIO
import os

from explorer import compare
from explorer import forms

@tag('compare')
class CompareTests(TestCase):
  def setUp(self):
    self.ref_taxid = '4751'
    self.ref_isotype = 'Asp'
    self.factory = RequestFactory()
    self.request = self.factory.get('')

  @classmethod
  def setUpClass(cls):
    super(CompareTests, cls).setUpClass()
    cls.formset = forms.CompareFormSet({
      'form-0-name': '', 'form-0-clade': '4751', 'form-0-isotype': 'Asp',
      'form-1-name': '', 'form-1-clade': '2759', 'form-1-isotype': 'All',
      'form-2-name': 'Test', 'form-2-clade': '4893', 'form-2-isotype': 'All',
      'form-TOTAL_FORMS': '3', 'form-MIN_NUM_FORMS': '0', 'form-MAX_NUM_FORMS': '1000', 'form-INITIAL_FORMS': '0'
      })
    
    cls.formset_json_fh = NamedTemporaryFile('w', buffering = 1)
    cls.formset_json = cls.formset_json_fh.name
    cls.formset_data = [form.as_dict() for form in cls.formset]
    cls.formset_json_fh.write(json.dumps(cls.formset_data))
    cls.formset_json_fh.flush()

    cls.factory = RequestFactory()
    cls.request = cls.factory.get(reverse('explorer:bitchart', kwargs = {'formset_json': cls.formset_json}))
    cls.seqs = compare.read_all_trnas()
    cls.trna_fasta_files = compare.write_trnas_to_files(cls.formset_data, cls.seqs)
    cls.ref_model_fh = compare.build_reference_model(cls.trna_fasta_files)
    cls.ref_bits = compare.calculate_normalizing_scores(cls.ref_model_fh)

    cls.bits = pd.DataFrame()
    for i, trna_fasta_fh in enumerate(cls.trna_fasta_files[1:]):
      current_bits = compare.align_trnas_collect_bit_scores(trna_fasta_fh.name, cls.formset_data[i + 2]['name'], cls.ref_model_fh.name)
      cls.bits = cls.bits.append(current_bits)
    cls.bits['score'] = round(cls.bits.apply(lambda x: x['score'] - cls.ref_bits[cls.ref_bits.position == x['position']]['score'].values[0], axis = 1), 2)

    ref_taxid = cls.formset_data[0]['clade']
    ref_isotype = cls.formset_data[0]['isotype']
    ref_cons = compare.get_cons_bits(ref_taxid, ref_isotype)
    ref_freqs = compare.get_modal_freqs(ref_taxid, ref_isotype)
    cls.bits = pd.concat([cls.bits, ref_cons, ref_freqs], sort = True).reset_index(drop = True)

  def test_compare_read_all_trnas(self):
    self.assertTrue(len(self.seqs) > 0)

  def test_compare_write_trnas_to_files(self):
    self.assertTrue(len(self.trna_fasta_files), 2)
    for i, file in enumerate(self.trna_fasta_files):
      with self.subTest(key = 'file-{}'.format(i)):
        seqs = [seq for seq in SeqIO.parse(file.name, 'fasta')]
        self.assertTrue(len(seqs) > 0)

  def test_compare_build_reference_model(self):
    model = self.ref_model_fh.read()
    self.assertIn(b'INFERNAL', model)
    self.assertIn(b'CM', model)
    self.assertIn(b'ROOT', model)

  def test_compare_calculate_normalizing_scores(self):
    self.assertIn('feature', self.ref_bits.columns)
    self.assertEqual(self.ref_bits.shape, (67, 4))
    self.assertEqual(len(self.ref_bits.seqname.unique()), 1)
    self.assertIn('CMCONSENSUS', self.ref_bits.seqname.unique()[0])

  def test_compare_align_trnas_collect_bit_scores(self):
    bits = compare.align_trnas_collect_bit_scores(self.trna_fasta_files[0].name, self.formset_data[2]['name'], self.ref_model_fh.name)
    self.assertEqual(bits.shape, (67, 5))
    self.assertIn('total', bits.columns)
    self.assertIn('group', bits.columns)
    self.assertEqual(bits.group.unique()[0], 'Test')

  def test_compare_get_cons_bits(self):
    ref_cons = compare.get_cons_bits(self.ref_taxid, self.ref_isotype)
    self.assertEqual(len(ref_cons.columns), 5)
    self.assertEqual(ref_cons.group[0], 'Reference consensus')

  def test_compare_get_modal_bits(self):
    ref_freqs = compare.get_modal_freqs(self.ref_taxid, self.ref_isotype)
    self.assertEqual(ref_freqs.shape, (132, 5))
    self.assertEqual(ref_freqs.group[0], 'Most common feature')

  def test_compare_check_bits_processed(self):
    groups = sorted(self.bits.group.unique())
    self.assertEqual(groups, ['Most common feature', 'Reference consensus', 'Test'])
    try:
      scores = self.bits.score.astype(float)
      self.assertEqual(len(scores), len(self.bits.score))
    except:
      self.fail('Could not cast score to float')

  def test_compare_format_bits_for_viz(self):
    plot_data = compare.format_bits_for_viz(self.bits)
    self.assertIn('bits', plot_data)
    self.assertEqual(plot_data['groups'], ['Reference consensus', 'Most common feature', 'Test'])
    bit_dict_keys = ['feature', 'group', 'label', 'position', 'score', 'total']
    for i, row in plot_data['bits'].items():
      self.assertEqual(sorted(row.keys()), bit_dict_keys)

  def test_compare_bitchart(self):
    # set temporary MEDIA_ROOT. test environment uses /tmp for tempfiles but production uses MEDIA_ROOT
    with self.settings(MEDIA_ROOT = ''):
      json_response = compare.bitchart(self.request, self.formset_json)
      plot_data = json.loads(json_response.content.decode('utf8'))

