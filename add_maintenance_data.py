import os
import django
import random
from datetime import date, timedelta
from decimal import Decimal

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ope_config.settings')
django.setup()

from fleet.vehicles.models import Vehiculo
from fleet.maintenance.models import Mantenimiento
from django.contrib.auth.models import User

def populate_maintenance():
    print("Iniciando creación de 10 solicitudes de mantenimiento...")
    
    # Obtener vehículos y un técnico (usuario admin)
    vehiculos = list(Vehiculo.objects.all())
    if not vehiculos:
        print("Error: No hay vehículos en la base de datos.")
        return
        
    admin_user = User.objects.filter(username='admin').first()
    
    descripciones = [
        "Cambio de aceite y filtros",
        "Revisión de frenos y pastillas",
        "Alineación y balanceo",
        "Revisión de sistema eléctrico",
        "Cambio de neumáticos delanteros",
        "Reparación de aire acondicionado",
        "Mantenimiento general preventivo",
        "Cambio de correa de repartición",
        "Revisión de suspensión",
        "Limpieza de inyectores"
    ]

    for i in range(10):
        v = random.choice(vehiculos)
        tipo = random.choice(['preventivo', 'correctivo'])
        estado = random.choice(['programado', 'realizado'])
        fecha = date.today() + timedelta(days=random.randint(-30, 30))
        
        m = Mantenimiento.objects.create(
            vehiculo=v,
            tecnico=admin_user,
            tipo=tipo,
            descripcion=descripciones[i % len(descripciones)],
            fecha=fecha,
            km_al_momento=v.km_acumulado + Decimal(random.randint(100, 500)),
            costo=Decimal(random.randint(50000, 500000)),
            estado=estado
        )
        print(f"Mantenimiento {m.id} creado para vehículo {v.placa} ({estado})")

    print("¡10 solicitudes de mantenimiento cargadas exitosamente!")

if __name__ == '__main__':
    populate_maintenance()
