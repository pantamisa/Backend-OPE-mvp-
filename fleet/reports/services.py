from django.db.models import Sum, Count, Avg
from fleet.contracts.models import Contrato
from fleet.maintenance.models import Mantenimiento
from .models import Reporte

class ReporteService:
    """
    Facade Pattern: Oculta la complejidad de las consultas al ORM
    y la generación de reportes detrás de una interfaz simple.
    """
    
    @staticmethod
    def generar_reporte_ingresos(vehiculo_id=None, desde=None, hasta=None):
        queryset = Contrato.objects.filter(estado='cerrada')
        
        if vehiculo_id:
            queryset = queryset.filter(vehiculo_id=vehiculo_id)
        if desde:
            queryset = queryset.filter(fecha_fin__gte=desde)
        if hasta:
            queryset = queryset.filter(fecha_fin__lte=hasta)
            
        stats = queryset.aggregate(
            ingresos_totales=Sum('costo_total'),
            num_rentas=Count('id'),
            promedio=Avg('costo_total')
        )
        
        resultado = {
            'ingresos_totales': float(stats['ingresos_totales'] or 0),
            'num_rentas': stats['num_rentas'],
            'promedio': float(stats['promedio'] or 0)
        }
        
        reporte = Reporte.objects.create(
            tipo='ingresos',
            parametros={'vehiculo_id': vehiculo_id, 'desde': desde, 'hasta': hasta},
            resultado=resultado
        )
        return reporte

    @staticmethod
    def generar_reporte_rentabilidad(vehiculo_id):
        ingresos = Contrato.objects.filter(vehiculo_id=vehiculo_id, estado='cerrada').aggregate(
            total=Sum('costo_total')
        )['total'] or 0
        
        costos = Mantenimiento.objects.filter(vehiculo_id=vehiculo_id, estado='realizado').aggregate(
            total=Sum('costo')
        )['total'] or 0
        
        resultado = {
            'ingresos_totales': float(ingresos),
            'costos_mantenimiento': float(costos),
            'rentabilidad_neta': float(ingresos - costos)
        }
        
        reporte = Reporte.objects.create(
            tipo='rentabilidad',
            parametros={'vehiculo_id': vehiculo_id},
            resultado=resultado
        )
        return reporte

    @staticmethod
    def exportar_pdf(reporte_id):
        # Lógica de exportación con ReportLab (Mocked for MVP scope)
        return f"/media/reportes/reporte_{reporte_id}.pdf"
