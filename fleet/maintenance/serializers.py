from rest_framework import serializers
from .models import Mantenimiento

class MantenimientoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mantenimiento
        fields = '__all__'
        read_only_fields = ['estado', 'created_at', 'updated_at', 'proximo_km', 'proximo_fecha']
