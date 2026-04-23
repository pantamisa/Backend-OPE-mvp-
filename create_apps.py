import os

apps = ['vehicles', 'drivers', 'contracts', 'maintenance', 'reports', 'alerts', 'telemetry']
os.makedirs('fleet', exist_ok=True)
with open('fleet/__init__.py', 'w') as f: pass

for app in apps:
    os.makedirs(f'fleet/{app}', exist_ok=True)
    with open(f'fleet/{app}/__init__.py', 'w') as f: pass
    with open(f'fleet/{app}/apps.py', 'w') as f:
        f.write(f"""from django.apps import AppConfig

class {app.capitalize()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fleet.{app}'
""")
