from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Contrato, Factura
from .serializers import ContratoSerializer, FacturaSerializer
from django.utils import timezone
import uuid

class ContratoViewSet(viewsets.ModelViewSet):
    queryset = Contrato.objects.all()
    serializer_class = ContratoSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Asignar un número de contrato único
        numero = f"CTR-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:4].upper()}"
        contrato = serializer.save(numero_contrato=numero, estado='activa')
        
        # Cambiar estado del vehículo
        vehiculo = contrato.vehiculo
        vehiculo.cambiar_estado('en_renta')

    @action(detail=True, methods=['patch'])
    def finalizar(self, request, pk=None):
        contrato = self.get_object()
        if contrato.estado != 'activa':
            return Response({'error': 'Solo se pueden cerrar rentas activas.'}, status=status.HTTP_400_BAD_REQUEST)

        km_final = request.data.get('km_final')
        if not km_final:
            return Response({'error': 'Debe proveer km_final.'}, status=status.HTTP_400_BAD_REQUEST)

        contrato.km_final = float(km_final)
        contrato.fecha_fin = timezone.now()
        
        # Calcular el costo usando el patrón Strategy
        costo_calculado = contrato.calcular_costo()
        contrato.costo_subtotal = costo_calculado
        contrato.costo_total = costo_calculado + contrato.costo_penalizaciones
        
        # Al guardar el contrato como 'cerrada', se disparan los Observers (signals)
        contrato.estado = 'cerrada'
        contrato.save()

        return Response({
            'status': 'Contrato finalizado exitosamente.',
            'costo_total': contrato.costo_total
        })

class FacturaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Factura.objects.all()
    serializer_class = FacturaSerializer
    permission_classes = [IsAuthenticated]
