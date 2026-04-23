from .models import Vehiculo

class AbstractVehiculoRepository:
    def get(self, id):
        raise NotImplementedError

    def save(self, vehiculo):
        raise NotImplementedError

    def list_available(self):
        raise NotImplementedError

class DjangoVehiculoRepository(AbstractVehiculoRepository):
    def get(self, id):
        try:
            return Vehiculo.objects.get(id=id)
        except Vehiculo.DoesNotExist:
            return None

    def save(self, vehiculo):
        vehiculo.save()
        return vehiculo

    def list_available(self):
        return Vehiculo.objects.filter(estado='disponible')
