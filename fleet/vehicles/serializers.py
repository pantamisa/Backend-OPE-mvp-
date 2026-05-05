from rest_framework import serializers
from .models import Vehiculo
from fleet.contracts.models import Contrato

class VehiculoSerializer(serializers.ModelSerializer):
    plate = serializers.CharField(source='placa')
    brand = serializers.CharField(source='marca')
    model = serializers.CharField(source='modelo')
    year = serializers.IntegerField(source='anio')
    type = serializers.CharField(source='get_tipo_display')
    status = serializers.CharField(source='get_estado_display')
    km_per_liter = serializers.SerializerMethodField()
    assigned_driver_name = serializers.SerializerMethodField()

    class Meta:
        model = Vehiculo
        fields = (
            'id', 'plate', 'brand', 'model', 'year', 'type', 
            'status', 'km_per_liter', 'assigned_driver_name'
        )

    def get_km_per_liter(self, obj):
        # Valor estático como en el ejemplo, o lógica de cálculo si existiera
        return 14.5

    def get_assigned_driver_name(self, obj):
        # Buscamos el contrato activo para este vehículo
        contrato_activo = Contrato.objects.filter(vehiculo=obj, estado='activa').first()
        if contrato_activo and contrato_activo.conductor:
            conductor = contrato_activo.conductor
            return f"{conductor.nombre} {conductor.apellido}"
        return None
