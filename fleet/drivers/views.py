from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Conductor
from .serializers import ConductorSerializer
from .repositories import DjangoConductorRepository

class ConductorViewSet(viewsets.ModelViewSet):
    queryset = Conductor.objects.all()
    serializer_class = ConductorSerializer
    permission_classes = [IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.repository = DjangoConductorRepository()
