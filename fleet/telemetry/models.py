from django.db import models
from fleet.vehicles.models import Vehiculo
from fleet.contracts.models import Contrato

class Telemetria(models.Model):
    id = models.BigAutoField(primary_key=True)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='telemetrias')
    contrato = models.ForeignKey(Contrato, on_delete=models.SET_NULL, null=True, blank=True)
    
    latitud = models.DecimalField(max_digits=10, decimal_places=7)
    longitud = models.DecimalField(max_digits=10, decimal_places=7)
    velocidad_kmh = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    km_acumulado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    nivel_combustible = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperatura_motor = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    raw_data = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'fleet_telemetria'
        indexes = [
            models.Index(fields=['vehiculo', '-timestamp']),
            models.Index(fields=['contrato']),
        ]

    def __str__(self):
        return f"Tel {self.vehiculo.placa} a {self.timestamp.strftime('%H:%M:%S')}"
