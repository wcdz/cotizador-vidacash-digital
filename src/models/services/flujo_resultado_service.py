from src.models.domain.flujo_resultado_domain import FlujoResultado
from src.common.producto import Producto
from src.infrastructure.repositories import get_repos
from typing import List


class FlujoResultadoService:

    def __init__(
        self,
        producto: Producto,
        cobertura: str,
        suma_asegurada: float,
        edad_actuarial: int,
        periodo_vigencia: int,
    ):
        self.flujo_resultado = FlujoResultado()
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
            return self.flujo_resultado.calcular_siniestros_fallecimiento(
                fallecidos, self.suma_asegurada
            )
        elif self.cobertura == "itp":
            repos = get_repos(producto=self.producto.value, cobertura=self.cobertura)
            tarifas_reaseguro = repos["tarifas_reaseguro"].get_tarifas_reaseguro()
            return self.flujo_resultado.calcular_siniestros_itp(
                vivos_inicio,
                self.suma_asegurada,
                self.edad_actuarial,
                self.periodo_vigencia,
                tarifas_reaseguro,
            )
        else:
            return 0
