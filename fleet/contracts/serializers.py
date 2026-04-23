from rest_framework import serializers
from .models import Contrato, Factura
from fleet.vehicles.models import Vehiculo
from fleet.drivers.models import Conductor

class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contrato
        fields = '__all__'
        read_only_fields = ['costo_subtotal', 'costo_total', 'estado', 'created_at', 'updated_at', 'km_final']

    def validate(self, data):
        vehiculo = data.get('vehiculo')
        conductor = data.get('conductor')

        # RN-01: El vehículo no puede tener más de una renta activa
        if Contrato.objects.filter(vehiculo=vehiculo, estado='activa').exists():
            raise serializers.ValidationError("RN-01: El vehículo ya tiene una renta activa.")

        # RN-04: El vehículo no puede tener mantenimiento pendiente
        if vehiculo.tiene_mantenimiento_pendiente():
            raise serializers.ValidationError("RN-04: El vehículo tiene mantenimiento pendiente.")

        # RN-07: El vehículo no puede estar fuera de servicio
        if vehiculo.estado == 'fuera_de_servicio':
            raise serializers.ValidationError("RN-07: El vehículo está fuera de servicio.")

        # RN-02: El conductor no puede exceder el límite diario (verificación inicial)
        if not conductor.puede_conducir():
            raise serializers.ValidationError("RN-02: El conductor ha excedido sus horas permitidas hoy o no está activo.")

        return data

class FacturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Factura
        fields = '__all__'
