from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Vehiculo
from .serializers import VehiculoSerializer
from .repositories import DjangoVehiculoRepository

class VehiculoViewSet(viewsets.ModelViewSet):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    permission_classes = [IsAuthenticated]

    # Inyección de dependencia para Repository Pattern
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repository = DjangoVehiculoRepository()

    def get_queryset(self):
        # Opcionalmente se podría usar self.repository.list_available() si se filtra,
        # pero para el ViewSet general usamos el ORM directamente o el repository extendido.
        return super().get_queryset()
