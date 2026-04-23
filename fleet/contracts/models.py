from django.db import models
from django.conf import settings
from fleet.vehicles.models import Vehiculo
from fleet.drivers.models import Conductor
from django.core.validators import MinValueValidator

class Contrato(models.Model):
    TIPO_TARIFA_CHOICES = [
        ('hora', 'Hora'),
        ('dia', 'Día'),
        ('km', 'Kilómetro'),
    ]

    ESTADO_CHOICES = [
        ('activa', 'Activa'),
        ('cerrada', 'Cerrada'),
        ('cancelada', 'Cancelada'),
    ]

    numero_contrato = models.CharField(max_length=25, unique=True)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.RESTRICT, related_name='contratos')
    conductor = models.ForeignKey(Conductor, on_delete=models.RESTRICT, related_name='contratos')
    creado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    tipo_tarifa = models.CharField(max_length=10, choices=TIPO_TARIFA_CHOICES, default='dia')
    tarifa_valor = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0.01)])
    
    km_inicial = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    km_final = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField(null=True, blank=True)
    
    costo_subtotal = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    costo_penalizaciones = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    costo_total = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='activa')
    observaciones = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fleet_contrato'
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['vehiculo']),
            models.Index(fields=['conductor']),
            models.Index(fields=['fecha_inicio']),
        ]

    def __str__(self):
        return f"{self.numero_contrato} - {self.vehiculo.placa}"

class Factura(models.Model):
    contrato = models.OneToOneField(Contrato, on_delete=models.RESTRICT, related_name='factura')
    numero_factura = models.CharField(max_length=25, unique=True)
    monto = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    fecha_emision = models.DateTimeField(auto_now_add=True)
    exportada = models.BooleanField(default=False)
    ruta_pdf = models.CharField(max_length=500, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'fleet_factura'
        indexes = [
            models.Index(fields=['fecha_emision']),
        ]

class Penalizacion(models.Model):
    TIPO_CHOICES = [
        ('exceso_horas', 'Exceso de horas'),
        ('zona_prohibida', 'Zona prohibida'),
        ('daño', 'Daño'),
        ('otro', 'Otro'),
    ]

    contrato = models.ForeignKey(Contrato, on_delete=models.CASCADE, related_name='penalizaciones')
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    descripcion = models.TextField()
    monto = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    fecha = models.DateTimeField(auto_now_add=True)
    registrado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'fleet_penalizacion'
        indexes = [
            models.Index(fields=['contrato']),
        ]
