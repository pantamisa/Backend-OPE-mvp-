from abc import ABC, abstractmethod
from decimal import Decimal
from django.utils import timezone
from .models import Mantenimiento

class MantenimientoService(ABC):
    """
    Template Method Pattern: Define el esqueleto del algoritmo de mantenimiento,
    delegando el cálculo del próximo mantenimiento a las subclases.
    """
    def ejecutar(self, vehiculo, datos_intervencion):
        self.validar_vehiculo(vehiculo)
        mantenimiento = self.registrar_intervencion(vehiculo, datos_intervencion)
        self.actualizar_historial(vehiculo)
        mantenimiento.proximo_km = self.calcular_proximo(mantenimiento)
        mantenimiento.save()
        return mantenimiento

    def validar_vehiculo(self, vehiculo):
        if vehiculo.estado == 'fuera_de_servicio':
            raise ValueError("No se puede hacer mantenimiento a un vehículo fuera de servicio.")

    def registrar_intervencion(self, vehiculo, datos):
        mantenimiento = Mantenimiento.objects.create(
            vehiculo=vehiculo,
            tipo=datos.get('tipo', 'preventivo'),
            descripcion=datos.get('descripcion', ''),
            fecha=datos.get('fecha', timezone.now().date()),
            km_al_momento=datos.get('km_al_momento', vehiculo.km_acumulado),
            costo=datos.get('costo', 0),
            estado='realizado'
        )
        return mantenimiento

    def actualizar_historial(self, vehiculo):
        # En la lógica real se actualizarían registros si es necesario
        vehiculo.cambiar_estado('disponible')

    @abstractmethod
    def calcular_proximo(self, mantenimiento) -> Decimal:
        pass

class MantenimientoPreventivo(MantenimientoService):
    def calcular_proximo(self, mantenimiento) -> Decimal:
        # Se programa para 5000 km después
        return mantenimiento.km_al_momento + Decimal('5000')

class MantenimientoCorrectivo(MantenimientoService):
    def calcular_proximo(self, mantenimiento) -> Decimal:
        # El mantenimiento correctivo no programa el siguiente por defecto
        return None
