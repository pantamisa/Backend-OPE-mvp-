import os
import django
import datetime
from django.utils import timezone
from decimal import Decimal

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ope_config.settings')
django.setup()

from django.contrib.auth.models import User
from fleet.vehicles.models import Vehiculo
from fleet.drivers.models import Conductor
from fleet.contracts.models import Contrato, Factura

def populate():
    print("Iniciando población de datos de prueba...")

    # 1. Crear Usuarios adicionales
    u1, created = User.objects.get_or_create(username='conductor1', email='c1@example.com')
    if created:
        u1.set_password('admin123')
        u1.first_name = 'Carlos'
        u1.last_name = 'Méndez'
        u1.save()

    u2, created = User.objects.get_or_create(username='conductor2', email='c2@example.com')
    if created:
        u2.set_password('admin123')
        u2.first_name = 'Ana'
        u2.last_name = 'García'
        u2.save()

    # 2. Crear Vehículos
    v1, _ = Vehiculo.objects.get_or_create(
        placa='ABC-123',
        defaults={
            'modelo': 'Sedán',
            'marca': 'Toyota',
            'anio': 2022,
            'tipo': 'particular',
            'capacidad': 5,
            'color': 'Blanco',
            'km_inicial': 0,
            'estado': 'disponible'
        }
    )

    v2, _ = Vehiculo.objects.get_or_create(
        placa='XYZ-789',
        defaults={
            'modelo': 'Furgón',
            'marca': 'Renault',
            'anio': 2021,
            'tipo': 'furgon',
            'capacidad': 2,
            'color': 'Gris',
            'km_inicial': 5000,
            'estado': 'mantenimiento'
        }
    )

    # 3. Crear Conductores
    c1, _ = Conductor.objects.get_or_create(
        cedula='123456789',
        defaults={
            'user': u1,
            'nombre': 'Carlos',
            'apellido': 'Méndez',
            'num_licencia': 'LIC-123',
            'categoria_licencia': 'B1',
            'telefono': '3001234567',
            'email': 'c1@example.com',
            'estado': 'activo'
        }
    )

    c2, _ = Conductor.objects.get_or_create(
        cedula='987654321',
        defaults={
            'user': u2,
            'nombre': 'Ana',
            'apellido': 'García',
            'num_licencia': 'LIC-456',
            'categoria_licencia': 'C1',
            'telefono': '3119876543',
            'email': 'c2@example.com',
            'estado': 'activo'
        }
    )

    # 4. Crear un Contrato Activo
    contrato_activo, created = Contrato.objects.get_or_create(
        numero_contrato='CONT-2026-001',
        defaults={
            'vehiculo': v1,
            'conductor': c1,
            'creado_por': User.objects.get(username='admin'),
            'tipo_tarifa': 'dia',
            'tarifa_valor': Decimal('150000.00'),
            'km_inicial': Decimal('100.00'),
            'fecha_inicio': timezone.now(),
            'estado': 'activa',
            'observaciones': 'Contrato de prueba activo'
        }
    )
    if created:
        v1.estado = 'en_renta'
        v1.save()

    # 5. Crear un Contrato Cerrado y su Factura
    fecha_ayer = timezone.now() - datetime.timedelta(days=1)
    contrato_cerrado, created = Contrato.objects.get_or_create(
        numero_contrato='CONT-2026-000',
        defaults={
            'vehiculo': v2,
            'conductor': c2,
            'creado_por': User.objects.get(username='admin'),
            'tipo_tarifa': 'dia',
            'tarifa_valor': Decimal('200000.00'),
            'km_inicial': Decimal('4800.00'),
            'km_final': Decimal('5000.00'),
            'fecha_inicio': fecha_ayer - datetime.timedelta(days=2),
            'fecha_fin': fecha_ayer,
            'costo_subtotal': Decimal('400000.00'),
            'costo_total': Decimal('400000.00'),
            'estado': 'cerrada'
        }
    )
    if created:
        Factura.objects.create(
            contrato=contrato_cerrado,
            numero_factura='FAC-2026-000',
            monto=Decimal('400000.00')
        )

    print("¡Datos de prueba cargados exitosamente!")

if __name__ == '__main__':
    populate()
