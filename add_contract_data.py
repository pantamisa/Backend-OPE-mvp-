import os
import django
import random
from datetime import timedelta
from django.utils import timezone
from decimal import Decimal

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ope_config.settings')
django.setup()

from fleet.vehicles.models import Vehiculo
from fleet.drivers.models import Conductor
from fleet.contracts.models import Contrato, Factura
from django.contrib.auth.models import User

def populate_contracts():
    print("Iniciando creación de 15 contratos...")
    
    vehiculos = list(Vehiculo.objects.all())
    conductores = list(Conductor.objects.all())
    admin_user = User.objects.filter(username='admin').first()

    if not vehiculos or not conductores:
        print("Error: Se necesitan vehículos y conductores en la base de datos.")
        return

    tipos_tarifa = ['hora', 'dia', 'km']
    
    for i in range(15):
        # Seleccionar vehículo y conductor al azar
        vehiculo = random.choice(vehiculos)
        conductor = random.choice(conductores)
        
        # Evitar crear contratos activos para vehículos que ya tienen uno
        if Contrato.objects.filter(vehiculo=vehiculo, estado='activa').exists():
            estado = 'cerrada'
        else:
            estado = random.choice(['activa', 'cerrada'])

        tipo_tarifa = random.choice(tipos_tarifa)
        tarifa_valor = Decimal(random.randint(50, 200)) * 1000 # 50k - 200k
        
        km_ini = vehiculo.km_acumulado
        # Si es cerrada, le ponemos fecha de fin y km final
        fecha_ini = timezone.now() - timedelta(days=random.randint(1, 10))
        fecha_fin = None
        km_fin = None
        
        if estado == 'cerrada':
            fecha_fin = fecha_ini + timedelta(days=random.randint(1, 5))
            km_fin = km_ini + Decimal(random.randint(50, 300))
        
        numero = f"CTR-SEED-{i:03d}"
        
        try:
            contrato = Contrato.objects.create(
                numero_contrato=numero,
                vehiculo=vehiculo,
                conductor=conductor,
                creado_por=admin_user,
                tipo_tarifa=tipo_tarifa,
                tarifa_valor=tarifa_valor,
                km_inicial=km_ini,
                km_final=km_fin,
                fecha_inicio=fecha_ini,
                fecha_fin=fecha_fin,
                estado=estado,
                costo_penalizaciones=Decimal('0.00') # Aseguramos que sea Decimal
            )
            
            if estado == 'activa':
                vehiculo.estado = 'en_renta'
                vehiculo.save()
            else:
                # Calcular costo para cerrados
                costo_calculado = contrato.calcular_costo()
                contrato.costo_subtotal = costo_calculado
                contrato.costo_total = costo_calculado + contrato.costo_penalizaciones
                contrato.save()
                
                # Crear factura
                Factura.objects.create(
                    contrato=contrato,
                    numero_factura=f"FAC-SEED-{i:03d}",
                    monto=contrato.costo_total
                )
            
            print(f"Contrato {numero} creado ({estado}) para {vehiculo.placa}")
            
        except Exception as e:
            print(f"Error creando contrato {numero}: {e}")

    print("¡15 contratos cargados exitosamente!")

if __name__ == '__main__':
    populate_contracts()
