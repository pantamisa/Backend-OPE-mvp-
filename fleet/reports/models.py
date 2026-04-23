from django.db import models
from django.conf import settings

class Reporte(models.Model):
    TIPO_CHOICES = [
        ('ingresos', 'Ingresos'),
        ('mantenimiento', 'Mantenimiento'),
        ('rentabilidad', 'Rentabilidad'),
        ('horas_conductor', 'Horas Conductor'),
    ]

    tipo = models.CharField(max_length=40, choices=TIPO_CHOICES)
    parametros = models.JSONField(default=dict)
    resultado = models.JSONField(null=True, blank=True)
    generado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    exportado = models.BooleanField(default=False)
    ruta_archivo = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'fleet_reporte'
        indexes = [
            models.Index(fields=['tipo']),
            models.Index(fields=['fecha_generacion']),
        ]

    def __str__(self):
        return f"Reporte {self.tipo} - {self.fecha_generacion.strftime('%Y-%m-%d')}"
