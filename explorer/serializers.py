from rest_framework import serializers

from . import models


class tRNASerializer(serializers.ModelSerializer):
  class Meta:
    model = models.tRNA
    fields = '__all__'