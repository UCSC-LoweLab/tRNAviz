from . import models
import django_filters

class tRNAFilter(django_filters.FilterSet):
    class Meta:
        model = models.tRNA
        fields = ['isotype', 'anticodon', 'genus', ]