from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg
from django.utils import timezone
from fleet.telemetry.models import Telemetria
from fleet.vehicles.models import Vehiculo

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        now = timezone.now()
        current_month = now.month
        current_year = now.year

        # 1. Consumo por coches (para el gráfico)
        # Agrupamos por vehículo y sumamos el nivel_combustible (usado como métrica de KW)
        consumo_por_coche = Vehiculo.objects.annotate(
            total_kw=Sum('telemetrias__nivel_combustible')
        ).values('placa', 'total_kw').order_by('placa')[:11]

        # 2. Consumo del mes
        consumo_mes = Telemetria.objects.filter(
            timestamp__month=current_month,
            timestamp__year=current_year
        ).aggregate(total=Sum('nivel_combustible'))['total'] or 0

        # 3. Promedio consumo mes
        promedio_mes = Telemetria.objects.filter(
            timestamp__month=current_month,
            timestamp__year=current_year
        ).aggregate(avg=Avg('nivel_combustible'))['avg'] or 0

        # 4. Promedio consumo en oficinas (Simulado o de un modelo específico si existiera)
        promedio_oficinas = 20.0 

        return Response({
            'labels': [item['placa'] for item in consumo_por_coche],
            'data': [float(item['total_kw'] or 0) for item in consumo_por_coche],
            'metrics': {
                'consumoMes': float(consumo_mes),
                'promedioMes': float(promedio_mes),
                'promedioOficinas': promedio_oficinas
            },
            'user': {
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            }
        })
