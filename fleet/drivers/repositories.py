from .models import Conductor

class AbstractConductorRepository:
    def get_by_cedula(self, cedula):
        raise NotImplementedError

    def save(self, conductor):
        raise NotImplementedError

class DjangoConductorRepository(AbstractConductorRepository):
    def get_by_cedula(self, cedula):
        try:
            return Conductor.objects.get(cedula=cedula)
        except Conductor.DoesNotExist:
            return None

    def save(self, conductor):
        conductor.save()
        return conductor
