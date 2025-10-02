from typing import Dict, Any
from src.models.services.flujo_resultado_service import FlujoResultadoService
from src.common.producto import Producto
from src.models.domain.gastos_domain import GastosDomain


class GastosService:

    def __init__(
        self,
        producto: Producto,
        cobertura: str,
        periodo_pago_primas: float,
        frecuencia_pago_primas: str,
        prima: float,
        fraccionamiento_primas: float,
        mantenimiento_poliza: float,
    ):
        self.gastos_domain = GastosDomain()
        self.flujo_resultado_service = FlujoResultadoService()
        self.periodo_pago_primas = periodo_pago_primas
        self.frecuencia_pago_primas = frecuencia_pago_primas
        self.prima = prima
        self.fraccionamiento_primas = fraccionamiento_primas
        self.producto = producto
        self.cobertura = cobertura
        self.mantenimiento_poliza = mantenimiento_poliza

    def calcular_gastos(self, expuestos_mes: Dict[int, Dict[str, Any]]):

        vivos_inicio = [expuestos_mes[mes]["vivos_inicio"] for mes in expuestos_mes]

        primas_recurrentes = self.flujo_resultado_service.calcular_primas_recurrentes(
            vivos_inicio,
            self.periodo_pago_primas,
            self.frecuencia_pago_primas,
            self.prima,
            self.fraccionamiento_primas,
        )

        gastos_mantenimiento_prima_co = (
            self.gastos_domain.calcular_gastos_mantenimiento_prima_co(
                primas_recurrentes, self.mantenimiento_poliza
            )
        )

        gastos_mantenimiento_moneda_poliza = 1

        gastos_mantenimiento_fijo_poliza_anual = 1

        factor_inflacion = 1

        gasto_mantenimiento_total = 1

        return 1
