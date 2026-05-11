from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum, Avg
from django.db.models.functions import ExtractMonth, ExtractYear
from django.utils import timezone
from fleet.telemetry.models import Telemetria
from fleet.vehicles.models import Vehiculo

class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        now = timezone.now()
        current_year = now.year
        current_month = now.month

        # 1. Consumo por Meses (Eje X del gráfico)
        labels = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        
        # Inicializamos los datos en 0.0 para cada mes
        data_meses = [0.0] * 12
        
        # Consultamos la telemetría del año actual, extrayendo el mes
        # Nota: Usamos ExtractMonth directamente sobre el queryset
        registros = Telemetria.objects.filter(timestamp__year=current_year)
        
        consumo_por_mes = registros.annotate(
            mes=ExtractMonth('timestamp')
        ).values('mes').annotate(
            total_consumo=Sum('nivel_combustible')
        ).order_by('mes')

        for item in consumo_por_mes:
            mes_index = item['mes'] - 1
            if 0 <= mes_index < 12:
                data_meses[mes_index] = float(item['total_consumo'] or 0)

        # 2. Métricas del mes actual
        # Consumo total de este mes
        stats_mes = Telemetria.objects.filter(
            timestamp__year=current_year,
            timestamp__month=current_month
        ).aggregate(
            total=Sum('nivel_combustible'),
            promedio=Avg('nivel_combustible')
        )

        return Response({
            'labels': labels,
            'data': data_meses,
            'metrics': {
                'consumoMes': float(stats_mes['total'] or 0),
                'promedioMes': round(float(stats_mes['promedio'] or 0), 2),
                'promedioOficinas': 20.0
            },
            'user': {
                'username': request.user.username,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
            }
        })
