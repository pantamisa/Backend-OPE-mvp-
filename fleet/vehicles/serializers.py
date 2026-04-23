from rest_framework import serializers
from .models import Vehiculo

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = '__all__'
        read_only_fields = ['fecha_registro', 'updated_at', 'km_acumulado']
