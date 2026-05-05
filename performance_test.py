import os
import django
import time
import statistics

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ope_config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken

# Permitir el host del cliente de prueba
if 'testserver' not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append('testserver')

def run_performance_test():
    print("Iniciando pruebas de rendimiento con Script Personalizado (JWT)...")
    client = Client()
    
    # 1. Preparar autenticación
    admin_user, created = User.objects.get_or_create(username='perf_admin', defaults={'is_staff': True, 'is_superuser': True})
    if created:
        admin_user.set_password('perf_password123')
        admin_user.save()
    
    # Generar Token JWT
    refresh = RefreshToken.for_user(admin_user)
    token = str(refresh.access_token)
    auth_header = f'Bearer {token}'
    
    endpoints = [
        '/api/vehicles/',
        '/api/drivers/',
        '/api/contracts/',
        '/api/telemetry/',
        '/api/alerts/',
        '/api/maintenance/'
    ]
    
    iterations = 50
    results = {}
    
    print(f"Ejecutando {iterations} iteraciones por endpoint...\n")
    
    for endpoint in endpoints:
        print(f"Probando: {endpoint} ", end="", flush=True)
        latencies = []
        for i in range(iterations):
            start_time = time.perf_counter()
            response = client.get(endpoint, HTTP_AUTHORIZATION=auth_header)
            end_time = time.perf_counter()
            
            if response.status_code == 200:
                latencies.append((end_time - start_time) * 1000) # ms
            else:
                print(f"x (Error {response.status_code}) ", end="", flush=True)
            
            if i % 10 == 0:
                print(".", end="", flush=True)
        
        if latencies:
            results[endpoint] = {
                'avg': statistics.mean(latencies),
                'min': min(latencies),
                'max': max(latencies)
            }
            print(" Hecho.")
        else:
            print(" Fallido.")
    
    # Reporte Final
    print("\n" + "="*60)
    print(f"{'Endpoint':<30} | {'Avg (ms)':<10} | {'Min':<8} | {'Max':<8}")
    print("-" * 60)
    for endpoint, data in results.items():
        print(f"{endpoint:<30} | {data['avg']:<10.2f} | {data['min']:<8.2f} | {data['max']:<8.2f}")
    print("="*60)

if __name__ == '__main__':
    run_performance_test()
