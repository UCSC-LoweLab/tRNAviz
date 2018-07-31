from django import forms
from . import models

ISOTYPES = ['Ala', 'Arg', 'Asn', 'Asp', 'Cys', 'Gln', 'Glu', 'Gly', 'His', 'Ile', 'iMet', 'Leu', 'Lys', 'Met', 'Phe', 'Pro', 'Ser', 'Thr', 'Trp', 'Tyr', 'Val']

class CompareGroupForm(forms.Form):
  name = forms.CharField(max_length = 10, required = True)
  input_fasta = forms.CharField(widget = forms.Textarea)
  clade = forms.ChoiceField(choices = [])
  isotype = forms.ChoiceField(choices = ISOTYPES)

  def __init__(self, *args, **kwargs):
    super(CompareQueryForm, self).__init__(*args, **kwargs)
    self.fields['clade'].choices = [(clade.taxid, '{} ({})'.format(clade.name, clade.rank)) for clade in models.Taxonomy.objects.all()]

class CompareForm(forms.Form):
  def __init__(self, *args, **kwargs):
    # self.user = kwargs.pop('user', None)
    super(CompareForm, self).__init__(*args, **kwargs)

    self.fields['reference_clade'] = forms.CharField(
                                    max_length=30,
                                    initial = self.user.first_name,
                                    widget=forms.TextInput(attrs={
                                        'placeholder': 'First Name',
                                    }))
      self.fields['last_name'] = forms.CharField(
                                      max_length=30,
                                      initial = self.user.last_name,
                                      widget=forms.TextInput(attrs={
                                          'placeholder': 'Last Name',
                                      }))