from django import forms
from . import models
from . import choices

CLADES = [(clade.taxid, '{} ({})'.format(clade.name, clade.rank)) for clade in models.Taxonomy.objects.all()]

class CompareForm(forms.Form):
  name = forms.CharField(max_length = 10, required = True)
  input_fasta = forms.CharField(widget = forms.Textarea)
  clade = forms.ChoiceField(choices = CLADES)
  isotype = forms.ChoiceField(choices = choices.ISOTYPES)

  def is_valid(self):
    valid = super(SignInForm, self).is_valid()
    if not valid: return valid

    # validate reference
    try:
      clade = models.Taxonomy.objects.get(taxid = self.cleaned_data['clade'])
    except models.Taxonomy.DoesNotExist:
      self._errors['no_clade'] = 'Invalid clade - does not exist'
      return False

    if self.cleaned_data['isotype'] not in ['All'] + [i[0] for i in choices.ISOTYPES]:
      self._errors['invalid_isotype'] = 'Invalid isotype'
