from django.db import models
from django.conf import settings

class Conductor(models.Model):
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    cedula = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200, default='', blank=True)
    num_licencia = models.CharField(max_length=30, unique=True)
    categoria_licencia = models.CharField(max_length=10, default='B1')
    fecha_venc_licencia = models.DateField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(max_length=254, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='activo')
    horas_hoy = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    horas_totales = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    limite_horas_dia = models.DecimalField(max_digits=4, decimal_places=2, default=8.00)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fleet_conductor'
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['cedula']),
        ]

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.cedula}"

    def puede_conducir(self):
        return self.estado == 'activo' and self.horas_hoy < self.limite_horas_dia

    def actualizar_horas(self, horas):
        self.horas_hoy += horas
        self.horas_totales += horas
        self.save()
