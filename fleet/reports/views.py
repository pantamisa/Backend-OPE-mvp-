from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Reporte
from .serializers import ReporteSerializer
from .services import ReporteService

class ReporteViewSet(viewsets.ModelViewSet):
    queryset = Reporte.objects.all()
    serializer_class = ReporteSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        tipo = request.data.get('tipo')
        vehiculo_id = request.data.get('vehiculo_id')

        # Uso del Patrón Facade
        if tipo == 'ingresos':
            reporte = ReporteService.generar_reporte_ingresos(vehiculo_id=vehiculo_id)
        elif tipo == 'rentabilidad':
            if not vehiculo_id:
                return Response({'error': 'vehiculo_id es requerido para rentabilidad'}, status=status.HTTP_400_BAD_REQUEST)
            reporte = ReporteService.generar_reporte_rentabilidad(vehiculo_id=vehiculo_id)
        else:
            return Response({'error': 'Tipo de reporte no soportado.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(reporte)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
