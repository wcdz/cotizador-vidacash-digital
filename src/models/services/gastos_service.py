from typing import Dict, Any
from src.models.services.flujo_resultado_service import FlujoResultadoService
from src.common.producto import Producto
from src.models.domain.gastos_domain import GastosDomain
from typing import List


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
        moneda: str,
        valor_dolar: float,
        valor_soles: float,
        tiene_asistencia: bool,
        costo_mensual_asistencia_funeraria: float,
        inflacion_mensual: float,
        periodo_vigencia: float,
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
        self.moneda = moneda
        self.valor_dolar = valor_dolar
        self.valor_soles = valor_soles
        self.tiene_asistencia = tiene_asistencia
        self.costo_mensual_asistencia_funeraria = costo_mensual_asistencia_funeraria
        self.inflacion_mensual = inflacion_mensual
        self.periodo_vigencia = periodo_vigencia

    def calcular_gastos(
        self, vivos_inicio: List[float], primas_recurrentes: List[float]
    ):

        gastos_mantenimiento_prima_co = (
            self.gastos_domain.calcular_gastos_mantenimiento_prima_co(
                primas_recurrentes, self.mantenimiento_poliza
            )
        )

        gastos_mantenimiento_moneda_poliza = (
            self.gastos_domain.calcular_gastos_mantenimiento_moneda_poliza(
                self.moneda,
                self.valor_dolar,
                self.valor_soles,
                self.tiene_asistencia,
                self.costo_mensual_asistencia_funeraria,
            )
        )

        gastos_mantenimiento_fijo_poliza_anual = (
            self.gastos_domain.calcular_gastos_mantenimiento_fijo_poliza_anual(
                vivos_inicio, gastos_mantenimiento_moneda_poliza
            )
        )

        factor_inflacion = self.gastos_domain.calcular_factor_inflacion(
            gastos_mantenimiento_prima_co,
            gastos_mantenimiento_fijo_poliza_anual,
            self.inflacion_mensual,
        )

        gastos_mantenimiento_total = (
            self.gastos_domain.calcular_gastos_mantenimiento_total(
                gastos_mantenimiento_prima_co,
                gastos_mantenimiento_fijo_poliza_anual,
                factor_inflacion,
                self.periodo_vigencia,
            )
        )

        return {
            "gastos_mantenimiento_prima_co": gastos_mantenimiento_prima_co,
            "gastos_mantenimiento_moneda_poliza": gastos_mantenimiento_moneda_poliza,
            "gastos_mantenimiento_fijo_poliza_anual": gastos_mantenimiento_fijo_poliza_anual,
            "factor_inflacion": factor_inflacion,
            "gastos_mantenimiento_total": gastos_mantenimiento_total,
        }
