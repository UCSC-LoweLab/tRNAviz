from rest_framework import serializers

from . import models


class tRNASerializer(serializers.ModelSerializer):
  class Meta:
    model = models.tRNA
    fields = '__all__'

class CoordSerializer(serializers.ModelSerializer):
  class Meta:
    model = models.Coord
    fields = '__all__'