from decimal import Decimal
from abc import ABC, abstractmethod
from django.utils import timezone

class TarifaStrategy(ABC):
    @abstractmethod
    def calcular(self, contrato) -> Decimal:
        pass

class TarifaHora(TarifaStrategy):
    def calcular(self, contrato) -> Decimal:
        fecha_fin = contrato.fecha_fin or timezone.now()
        horas_transcurridas = Decimal((fecha_fin - contrato.fecha_inicio).total_seconds() / 3600)
        # Minimum 1 hour
        horas_transcurridas = max(Decimal(1.0), horas_transcurridas)
        return contrato.tarifa_valor * horas_transcurridas

class TarifaDia(TarifaStrategy):
    def calcular(self, contrato) -> Decimal:
        fecha_fin = contrato.fecha_fin or timezone.now()
        dias_completos = Decimal((fecha_fin.date() - contrato.fecha_inicio.date()).days)
        # Minimum 1 day
        dias_completos = max(Decimal(1.0), dias_completos)
        return contrato.tarifa_valor * dias_completos

class TarifaKm(TarifaStrategy):
    def calcular(self, contrato) -> Decimal:
        if contrato.km_final is None:
            # If not finished, can't precisely calculate km based, but could fallback to 0 or current
            return Decimal(0)
        km_recorridos = contrato.km_final - contrato.km_inicial
        return contrato.tarifa_valor * km_recorridos

class StrategyFactory:
    @staticmethod
    def get_strategy(tipo_tarifa: str) -> TarifaStrategy:
        if tipo_tarifa == 'hora':
            return TarifaHora()
        elif tipo_tarifa == 'dia':
            return TarifaDia()
        elif tipo_tarifa == 'km':
            return TarifaKm()
        else:
            raise ValueError(f"Tipo de tarifa desconocido: {tipo_tarifa}")
