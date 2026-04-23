from django.db import models
from django.conf import settings
from fleet.vehicles.models import Vehiculo
from django.core.validators import MinValueValidator

class Mantenimiento(models.Model):
    TIPO_CHOICES = [
        ('preventivo', 'Preventivo'),
        ('correctivo', 'Correctivo'),
    ]

    ESTADO_CHOICES = [
        ('programado', 'Programado'),
        ('realizado', 'Realizado'),
        ('cancelado', 'Cancelado'),
    ]

    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.RESTRICT, related_name='mantenimientos')
    tecnico = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='preventivo')
    descripcion = models.TextField(null=True, blank=True)
    fecha = models.DateField()
    km_al_momento = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    costo = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    
    proximo_km = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    proximo_fecha = models.DateField(null=True, blank=True)
    
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='programado')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fleet_mantenimiento'
        indexes = [
            models.Index(fields=['vehiculo']),
            models.Index(fields=['estado']),
            models.Index(fields=['fecha']),
        ]

    def __str__(self):
        return f"{self.tipo} - {self.vehiculo.placa} ({self.fecha})"
