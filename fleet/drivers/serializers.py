from rest_framework import serializers
from .models import Conductor

class ConductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conductor
        fields = '__all__'
        read_only_fields = ['horas_hoy', 'horas_totales', 'fecha_registro', 'updated_at']
