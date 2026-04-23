from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Alerta
from .serializers import AlertaSerializer
from django.utils import timezone

class AlertaViewSet(viewsets.ModelViewSet):
    queryset = Alerta.objects.all()
    serializer_class = AlertaSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['patch'])
    def resolver(self, request, pk=None):
        alerta = self.get_object()
        if alerta.resuelta:
            return Response({'error': 'La alerta ya está resuelta.'}, status=status.HTTP_400_BAD_REQUEST)

        alerta.resuelta = True
        alerta.fecha_resolucion = timezone.now()
        alerta.resuelta_por = request.user
        alerta.save()
        
        return Response({'status': 'Alerta resuelta.'})
