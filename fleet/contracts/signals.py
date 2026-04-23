from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Contrato, Factura
from fleet.alerts.models import Alerta

@receiver(post_save, sender=Contrato)
def contrato_cerrado_observer(sender, instance, created, **kwargs):
    """
    Observer Pattern: Cuando un contrato se guarda, si su estado cambia a 'cerrada',
    se disparan varios efectos secundarios.
    """
    if not created and instance.estado == 'cerrada':
        # 1. Generar Factura si no existe
        if not hasattr(instance, 'factura'):
            Factura.objects.create(
                contrato=instance,
                numero_factura=f"FAC-{timezone.now().strftime('%Y%m%d')}-{instance.id:04d}",
                monto=instance.costo_total or 0
            )

        # 2. Actualizar horas del conductor y generar alerta si excede (RN-02)
        if instance.fecha_fin and instance.fecha_inicio:
            horas_transcurridas = (instance.fecha_fin - instance.fecha_inicio).total_seconds() / 3600
            conductor = instance.conductor
            conductor.actualizar_horas(horas_transcurridas)

            if conductor.horas_hoy > conductor.limite_horas_dia:
                Alerta.objects.create(
                    tipo='exceso_horas',
                    vehiculo=instance.vehiculo,
                    conductor=conductor,
                    contrato=instance,
                    mensaje=f"El conductor excedió su límite de {conductor.limite_horas_dia} horas hoy.",
                    prioridad='alta'
                )

        # 3. Liberar el vehículo
        vehiculo = instance.vehiculo
        vehiculo.cambiar_estado('disponible')
        if instance.km_final:
            vehiculo.km_acumulado += (instance.km_final - instance.km_inicial)
            vehiculo.save()
