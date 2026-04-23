from django.db import models
from django.core.validators import MinValueValidator

class Vehiculo(models.Model):
    TIPO_CHOICES = [
        ('particular', 'Particular'),
        ('bus', 'Bus'),
        ('camion', 'Camión'),
        ('motocicleta', 'Motocicleta'),
        ('furgon', 'Furgón'),
    ]

    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('en_renta', 'En Renta'),
        ('mantenimiento', 'Mantenimiento'),
        ('fuera_de_servicio', 'Fuera de Servicio'),
    ]

    placa = models.CharField(max_length=10, unique=True)
    modelo = models.CharField(max_length=100)
    marca = models.CharField(max_length=80, default='', blank=True)
    anio = models.SmallIntegerField(validators=[MinValueValidator(1900)])
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='particular')
    capacidad = models.SmallIntegerField(default=1, validators=[MinValueValidator(1)])
    color = models.CharField(max_length=40, null=True, blank=True)
    numero_motor = models.CharField(max_length=50, null=True, blank=True)
    numero_chasis = models.CharField(max_length=50, null=True, blank=True)
    km_inicial = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    km_acumulado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=25, choices=ESTADO_CHOICES, default='disponible')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fleet_vehiculo'
        indexes = [
            models.Index(fields=['estado']),
        ]

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo}"

    def cambiar_estado(self, nuevo_estado):
        self.estado = nuevo_estado
        self.save()

    def calcular_km_totales(self):
        return self.km_acumulado

    def tiene_mantenimiento_pendiente(self):
        # Será implementado usando el repository o importando Mantenimiento si es necesario
        # o mediante consulta inversa
        return self.mantenimientos.filter(estado='programado').exists()
