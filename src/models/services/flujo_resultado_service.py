from src.models.domain.flujo_resultado_domain import FlujoResultado
from src.common.producto import Producto
from src.infrastructure.repositories import get_repos
from typing import List
from src.models.services.reserva_service import ReservaService


class FlujoResultadoService:

    def __init__(
        self,
        producto: Producto,
        cobertura: str,
        suma_asegurada: float,
        edad_actuarial: int,
        periodo_vigencia: int,
        prima: float,
        fraccionamiento_primas: float,
        porcentaje_devolucion: float,
    ):
        self.flujo_resultado = FlujoResultado()
        self.reserva_service = ReservaService(
            producto=producto,
            cobertura=cobertura,
            periodo_vigencia=periodo_vigencia,
            prima=prima,
            fraccionamiento_primas=fraccionamiento_primas,
            porcentaje_devolucion=porcentaje_devolucion,
        )
        self.producto = producto
        self.cobertura = cobertura
        self.suma_asegurada = suma_asegurada
        self.edad_actuarial = edad_actuarial
        self.periodo_vigencia = periodo_vigencia

    def calcular_primas_recurrentes(
        self,
        vivos_inicio: float,
        periodo_pago_primas: float,
        frecuencia_pago_primas: str,
        prima: float,
        fraccionamiento_primas: float,
    ):
        return self.flujo_resultado.calcular_primas_recurrentes(
            vivos_inicio,
            periodo_pago_primas,
            frecuencia_pago_primas,
            prima,
            fraccionamiento_primas,
        )

    def calcular_siniestros(self, fallecidos: List[float], vivos_inicio: List[float]):
        if self.cobertura == "fallecimiento":
            siniestros_fallecimiento = (
                self.flujo_resultado.calcular_siniestros_fallecimiento(
                    fallecidos, self.suma_asegurada
                )
            )
            return [-valor for valor in siniestros_fallecimiento]
        elif self.cobertura == "itp":
            repos = get_repos(producto=self.producto.value, cobertura=self.cobertura)
            tarifas_reaseguro = repos["tarifas_reaseguro"].get_tarifas_reaseguro()
            siniestros_itp = self.flujo_resultado.calcular_siniestros_itp(
                vivos_inicio,
                self.suma_asegurada,
                self.edad_actuarial,
                self.periodo_vigencia,
                tarifas_reaseguro,
            )
            return [-valor for valor in siniestros_itp]
        else:
            return 0

    def calcular_rescate(self, caducados: List[float], rescates: List[float]):
        rescate_ajuste_devolucion = (
            self.reserva_service.calcular_rescate_ajuste_devolucion(caducados, rescates)
        )
        return [-valor for valor in rescate_ajuste_devolucion]
