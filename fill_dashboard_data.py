import os
import django
import random
from datetime import datetime
from django.utils import timezone
from decimal import Decimal

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ope_config.settings')
django.setup()

from fleet.vehicles.models import Vehiculo
from fleet.telemetry.models import Telemetria

def fill_annual_dashboard():
    print("Iniciando generación de datos para los 12 meses...")
    
    vehiculos = list(Vehiculo.objects.all())
    if not vehiculos:
        print("Error: No hay vehículos para generar telemetría.")
        return

    current_year = timezone.now().year
    
    # Limpiamos datos previos para ver el gráfico nuevo con claridad
    Telemetria.objects.all().delete()

    for mes in range(1, 13):
        # Generar entre 15 y 30 registros por mes para crear picos y valles
        num_registros = random.randint(15, 30)
        print(f"Generando {num_registros} registros para el mes {mes}...")
        
        for _ in range(num_registros):
            v = random.choice(vehiculos)
            
            # Fecha aleatoria en el mes
            dia = random.randint(1, 28)
            fecha_fake = datetime(current_year, mes, dia, 12, 0, tzinfo=timezone.get_current_timezone())
            
            Telemetria.objects.create(
                vehiculo=v,
                latitud=Decimal("6.21"),
                longitud=Decimal("-75.56"),
                velocidad_kmh=Decimal(random.randint(20, 90)),
                km_acumulado=Decimal(random.randint(1000, 5000)),
                nivel_combustible=Decimal(random.randint(50, 400)), # Usado como KW
                timestamp=fecha_fake
            )

    print("¡Proceso completado! Los 12 meses ahora tienen datos aleatorios.")

if __name__ == '__main__':
    fill_annual_dashboard()
