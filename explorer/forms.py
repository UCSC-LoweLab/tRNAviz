from django import forms
from django.forms import formset_factory
from . import models
from . import choices

CLADES = [(clade.taxid, '{} ({})'.format(clade.name, clade.rank)) for clade in models.Taxonomy.objects.all()]

class CompareForm(forms.Form):
  name = forms.CharField(max_length = 10, required = False)
  input_fasta = forms.CharField(widget = forms.Textarea, required = False)
  clade = forms.ChoiceField(choices = CLADES, required = False)
  isotype = forms.ChoiceField(choices = choices.ISOTYPES, required = False)

  def is_valid(self):
    valid = super(CompareForm, self).is_valid()
    if not valid: return valid
    print(self.cleaned_data)
    # validate clade
    try:
      clade = models.Taxonomy.objects.get(taxid = self.cleaned_data['clade'])
    except models.Taxonomy.DoesNotExist:
      self.add_error('clade', 'Invalid clade - does not exist in database')
      return False

    return True

CompareFormset = formset_factory(CompareForm, extra = 3)