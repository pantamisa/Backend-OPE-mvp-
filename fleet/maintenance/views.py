from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Mantenimiento
from .serializers import MantenimientoSerializer
from .services import MantenimientoPreventivo, MantenimientoCorrectivo
from fleet.vehicles.models import Vehiculo

class MantenimientoViewSet(viewsets.ModelViewSet):
    queryset = Mantenimiento.objects.all()
    serializer_class = MantenimientoSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Usamos el Patrón Template Method
        tipo = request.data.get('tipo', 'preventivo')
        vehiculo_id = request.data.get('vehiculo')
        
        try:
            vehiculo = Vehiculo.objects.get(id=vehiculo_id)
        except Vehiculo.DoesNotExist:
            return Response({'error': 'Vehículo no encontrado'}, status=status.HTTP_404_NOT_FOUND)

        if tipo == 'preventivo':
            servicio = MantenimientoPreventivo()
        else:
            servicio = MantenimientoCorrectivo()

        try:
            # El Template Method 'ejecutar' hace toda la lógica (validar, registrar, actualizar historial, calcular próximo)
            mantenimiento = servicio.ejecutar(vehiculo, request.data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(mantenimiento)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
