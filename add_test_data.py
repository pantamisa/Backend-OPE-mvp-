import os
import django
import random
from django.utils import timezone
from decimal import Decimal

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ope_config.settings')
django.setup()

from fleet.vehicles.models import Vehiculo
from fleet.telemetry.models import Telemetria

def populate_30_vehicles():
    print("Iniciando creación de 30 vehículos y telemetría...")

    marcas = ['Toyota', 'Renault', 'Chevrolet', 'Ford', 'Hyundai', 'Nissan', 'Kia', 'Mazda']
    modelos = ['Sedán', 'Bus', 'Camión', 'Camioneta', 'Furgón', 'Hatchback']
    tipos = ['particular', 'bus', 'camion', 'furgon']

    for i in range(1, 31):
        placa = f"TEST-{i:03d}"
        v, created = Vehiculo.objects.get_or_create(
            placa=placa,
            defaults={
                'modelo': random.choice(modelos),
                'marca': random.choice(marcas),
                'anio': random.randint(2015, 2024),
                'tipo': random.choice(tipos),
                'capacidad': random.randint(2, 40),
                'color': random.choice(['Blanco', 'Gris', 'Negro', 'Azul', 'Rojo']),
                'km_inicial': random.randint(0, 10000),
                'estado': 'disponible'
            }
        )
        
        if created:
            print(f"Vehículo {placa} creado.")
        
        # Crear 10 entradas de telemetría para cada vehículo para que el dashboard tenga datos
        for j in range(10):
            Telemetria.objects.create(
                vehiculo=v,
                latitud=Decimal(f"6.2{random.randint(1000, 9999)}"),
                longitud=Decimal(f"-75.5{random.randint(1000, 9999)}"),
                velocidad_kmh=Decimal(random.randint(0, 100)),
                km_acumulado=v.km_acumulado + Decimal(j * 5),
                nivel_combustible=Decimal(random.randint(5, 30)), # Usado como KW en el dashboard
                timestamp=timezone.now()
            )

    print("¡30 vehículos y sus datos de telemetría han sido cargados!")

if __name__ == '__main__':
    populate_30_vehicles()
