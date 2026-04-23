from django.db import models
from django.conf import settings
from fleet.vehicles.models import Vehiculo
from fleet.drivers.models import Conductor
from fleet.contracts.models import Contrato

class Alerta(models.Model):
    TIPO_CHOICES = [
        ('exceso_horas', 'Exceso de Horas'),
        ('mantenimiento_proximo', 'Mantenimiento Próximo'),
        ('zona_prohibida', 'Zona Prohibida'),
        ('bajo_rendimiento', 'Bajo Rendimiento'),
        ('falla_sensor', 'Falla en Sensor'),
    ]

    PRIORIDAD_CHOICES = [
        ('alta', 'Alta'),
        ('media', 'Media'),
        ('baja', 'Baja'),
    ]

    tipo = models.CharField(max_length=40, choices=TIPO_CHOICES)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, null=True, blank=True)
    conductor = models.ForeignKey(Conductor, on_delete=models.SET_NULL, null=True, blank=True)
    contrato = models.ForeignKey(Contrato, on_delete=models.SET_NULL, null=True, blank=True)
    
    mensaje = models.TextField()
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    resuelta = models.BooleanField(default=False)
    
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    fecha_resolucion = models.DateTimeField(null=True, blank=True)
    resuelta_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'fleet_alerta'
        indexes = [
            models.Index(fields=['vehiculo']),
            models.Index(fields=['resuelta']),
            models.Index(fields=['tipo']),
            models.Index(fields=['-fecha_generacion']),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.get_prioridad_display()}"
