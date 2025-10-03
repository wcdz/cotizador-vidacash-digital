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

    def calcular_gastos_mantenimiento(self, gastos_mantenimiento_total: List[float]):
        return self.flujo_resultado.calcular_gastos_mantenimiento(
            gastos_mantenimiento_total
        )

    def calcular_gastos_adquisicion(self, gasto_adquisicion: float):
        return self.flujo_resultado.calcular_gastos_adquisicion(gasto_adquisicion)

    def calcular_comision(
        self,
        primas_recurrentes: List[float],
        vivos_inicio: List[float],
        frecuencia_pago_primas: str,
        tiene_asistencia: bool,
        costo_mensual_asistencia_funeraria: float,
        comision: float,
    ):
        return self.flujo_resultado.calcular_comision(
            primas_recurrentes,
            vivos_inicio,
            frecuencia_pago_primas,
            tiene_asistencia,
            costo_mensual_asistencia_funeraria,
            comision,
        )

    def calcular_variacion_reserva(
        self, varianza_reserva: List[float], varianza_moce: List[float]
    ):
        return self.flujo_resultado.calcular_variacion_reserva(
            varianza_reserva, varianza_moce
        )

    def calcular_utilidad_pre_pi_ms(
        self,
        primas_recurrentes: List[float],
        comision: List[float],
        gastos_mantenimiento: List[float],
        gastos_adquisicion: List[float],
        siniestros: List[float],
        rescate_ajuste_devolucion: List[float],
        variacion_reserva: List[float],
    ):
        return self.flujo_resultado.calcular_utilidad_pre_pi_ms(
            primas_recurrentes,
            comision,
            gastos_mantenimiento,
            gastos_adquisicion,
            siniestros,
            rescate_ajuste_devolucion,
            variacion_reserva,
        )

    def calcular_variacion_margen_solvencia(
        self, varianza_margen_solvencia: List[float]
    ):
        return [-valor for valor in varianza_margen_solvencia]

    def calcular_IR(self, utilidad_pre_pi_ms: List[float], impuesto_renta: float):
        return self.flujo_resultado.calcular_IR(utilidad_pre_pi_ms, impuesto_renta)

    def calcular_producto_inversion(self, ingreso_total_inversiones: List[float]):
        return ingreso_total_inversiones

    def calcular_flujo_resultado(
        self,
        utilidad_pre_pi_ms: List[float],
        variacion_margen_solvencia: List[float],
        IR: List[float],
        producto_inversion: List[float],
    ):
        return self.flujo_resultado.calcular_flujo_resultado(
            utilidad_pre_pi_ms, variacion_margen_solvencia, IR, producto_inversion
        )

    def calcular_vna_resultado(
        self, flujo_resultado: List[float], tasa_costo_capital_mes: float
    ):
        return self.flujo_resultado.calcular_vna_resultado(
            flujo_resultado, tasa_costo_capital_mes
        )
