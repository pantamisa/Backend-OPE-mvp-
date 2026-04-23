from rest_framework import serializers
from .models import Reporte

class ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporte
        fields = '__all__'
        read_only_fields = ['resultado', 'fecha_generacion', 'exportado', 'ruta_archivo']
