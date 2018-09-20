from django.test import TestCase, Client, tag, RequestFactory
from django.urls import reverse

from tempfile import NamedTemporaryFile
import json
from Bio import SeqIO

from explorer import compare
from explorer import forms


@tag('current')
class CompareTests(TestCase):
  def setUp(self):
    self.formset = forms.CompareFormSet({
      'form-0-name': '', 'form-0-clade': '4751', 'form-0-isotype': 'Asp',
      'form-1-name': '', 'form-1-clade': '2759', 'form-1-isotype': 'All',
      'form-2-name': 'Test', 'form-2-clade': '4893', 'form-2-isotype': 'All',
      'form-TOTAL_FORMS': '3', 'form-MIN_NUM_FORMS': '0', 'form-MAX_NUM_FORMS': '1000', 'form-INITIAL_FORMS': '0'
      })
    
    formset_json_fh = NamedTemporaryFile('w')
    self.formset_json = formset_json_fh.name
    self.formset_data = [form.as_dict() for form in self.formset]
    formset_json_fh.write(json.dumps(self.formset_data))
    formset_json_fh.close()
    self.factory = RequestFactory()
    self.request = self.factory.get(reverse('explorer:bitchart', kwargs = {'formset_json': self.formset_json}))
    self.seqs = compare.read_all_trnas()
    self.trna_fasta_files = compare.write_trnas_to_files(self.formset_data, self.seqs)

  def test_compare_read_all_trnas(self):
    self.assertTrue(len(self.seqs) > 0)

  def test_compare_write_trnas_to_files(self):
    self.assertTrue(len(self.trna_fasta_files), 2)
    for i, file in enumerate(self.trna_fasta_files):
      with self.subTest(key = 'file-{}'.format(i)):
        seqs = [seq for seq in SeqIO.parse(file.name, 'fasta')]
        self.assertTrue(len(seqs) > 0)


  # def test_compare_build_reference_model(self):
  #   pass

  # @tag('not-done')
  # def test_compare_bitchart(self):
  #   json_response = services.distribution(self.request, self.formset_json_filename)
  #   plot_data = json.loads(json_response.content.decode('utf8'))
  #   self.assertEqual(type(plot_data), dict)
  #   self.assertTrue(len(plot_data) > 0)

