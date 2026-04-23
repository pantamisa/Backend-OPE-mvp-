from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Telemetria
from .serializers import TelemetriaSerializer

class TelemetriaViewSet(viewsets.ModelViewSet):
    queryset = Telemetria.objects.all()
    serializer_class = TelemetriaSerializer
    permission_classes = [IsAuthenticated]

    # Aquí podríamos agregar validaciones adicionales para ingestion de datos masivos si fuera necesario
