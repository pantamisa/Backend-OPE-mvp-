import os
import django
import random
from django.utils import timezone
from datetime import date, timedelta

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ope_config.settings')
django.setup()

from django.contrib.auth.models import User
from fleet.drivers.models import Conductor

def populate_drivers():
    print("Iniciando creación de 15 conductores...")
    
    nombres = ['Juan', 'Pedro', 'Maria', 'Luisa', 'Ricardo', 'Elena', 'Diego', 'Paula', 'Andrés', 'Sofía', 'Gabriel', 'Valentina', 'Mateo', 'Isabella', 'Nicolás']
    apellidos = ['Pérez', 'Gómez', 'Rodríguez', 'López', 'Martínez', 'Sánchez', 'Torres', 'Ramírez', 'Hernández', 'Díaz', 'Morales', 'Castillo', 'Ortega', 'Vargas', 'Ríos']
    categorias = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

    for i in range(15):
        nombre = nombres[i % len(nombres)]
        apellido = apellidos[i % len(apellidos)]
        username = f"conductor_{random.randint(1000, 9999)}_{i}"
        email = f"{username}@example.com"
        cedula = f"{random.randint(10000000, 99999999)}"
        licencia = f"LIC-{random.randint(100000, 999999)}"
        
        # Crear usuario de Django primero
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': nombre,
                'last_name': apellido
            }
        )
        if created:
            user.set_password('driver123')
            user.save()

        # Crear conductor asociado
        conductor, created = Conductor.objects.get_or_create(
            cedula=cedula,
            defaults={
                'user': user,
                'nombre': nombre,
                'apellido': apellido,
                'num_licencia': licencia,
                'categoria_licencia': random.choice(categorias),
                'fecha_venc_licencia': date.today() + timedelta(days=random.randint(365, 1825)),
                'telefono': f"3{random.randint(00, 22)}{random.randint(1000000, 9999999)}",
                'email': email,
                'estado': 'activo',
                'limite_horas_dia': 8.00
            }
        )
        
        if created:
            print(f"Conductor {nombre} {apellido} (Cédula: {cedula}) creado.")
        else:
            print(f"Conductor con cédula {cedula} ya existía.")

    print("¡15 conductores cargados exitosamente!")

if __name__ == '__main__':
    populate_drivers()
