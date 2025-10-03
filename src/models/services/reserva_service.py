from src.models.domain.reserva_domain import ReservaDomain
from src.common.producto import Producto
from src.infrastructure.repositories import get_repos
from typing import List


class ReservaService:

    def __init__(
        self,
        producto: Producto,
        cobertura: str,
        periodo_vigencia: int,
        prima: float,
        fraccionamiento_primas: float,
        porcentaje_devolucion: float,
    ):
        self.producto = producto
        self.cobertura = cobertura
        self.periodo_vigencia = periodo_vigencia
        self.prima = prima
        self.fraccionamiento_primas = fraccionamiento_primas
        self.porcentaje_devolucion = porcentaje_devolucion

        repos = get_repos(producto=self.producto.value, cobertura=self.cobertura)
        self.matriz_devolucion = repos[
            "devolucion"
        ].get_devolucion_by_producto_and_cobertura(
            producto=self.producto.value, cobertura=self.cobertura
        )

        self.reserva = ReservaDomain(
            periodo_vigencia=periodo_vigencia,
            matriz_devolucion=self.matriz_devolucion,
            prima=prima,
            fraccionamiento_primas=fraccionamiento_primas,
            porcentaje_devolucion=porcentaje_devolucion,
        )

    def calcular_rescate(self):
        return self.reserva.calcular_rescate()

    def calcular_rescate_ajuste_devolucion(
        self, caducados: List[float], rescates: List[float]
    ):
        return self.reserva.calcular_rescate_ajuste_devolucion(caducados, rescates)

    def calcular_flujo_pasivo(
        self,
        primas_recurrentes: List[float],
        siniestros: List[float],
        rescate_ajuste_devolucion: List[float],
        gastos_mantenimiento: List[float],
        gastos_adquisicion: List[float],
        comision: List[float],
    ):
        return self.reserva.calcular_flujo_pasivo(
            primas_recurrentes,
            siniestros,
            rescate_ajuste_devolucion,
            gastos_mantenimiento,
            gastos_adquisicion,
            comision,
        )

    def calcular_saldo_reserva(
        self,
        vivos_inicio: List[float],
        rescate: List[float],
        flujo_pasivo: List[float],
        tasa_interes_mensual: float,
    ):
        return self.reserva.calcular_saldo_reserva(
            vivos_inicio, rescate, flujo_pasivo, tasa_interes_mensual
        )

    def calcular_moce(
        self,
        tasa_costo_capital_mensual: float,
        tasa_interes_mensual: float,
        margen_solvencia: float,
        saldo_reserva: List[float],
    ):
        return self.reserva.calcular_moce(
            tasa_costo_capital_mensual,
            tasa_interes_mensual,
            margen_solvencia,
            saldo_reserva,
        )

    def calcular_moce_saldo_reserva(
        self, saldo_reserva: List[float], moce: List[float]
    ):
        return self.reserva.calcular_moce_saldo_reserva(saldo_reserva, moce)
    
    def calcular_varianza_moce(self, moce: List[float]):
        return self.reserva.calcular_varianza_moce(moce)
    
    def calcular_varianza_reserva(self, saldo_reserva: List[float]):
        return self.reserva.calcular_varianza_reserva(saldo_reserva)