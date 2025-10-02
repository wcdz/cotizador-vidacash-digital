from src.models.domain.parametros_calculados import ParametrosCalculados
from src.common.producto import Producto
from src.common.frecuencia_pago import FrecuenciaPago
from src.infrastructure.repositories import get_repos
from typing import Dict, Any


class ParametrosCalculadosService:

    def __init__(self):
        self.parametros_calculados = ParametrosCalculados()
        self._factores_pago = None

    def _cargar_factores_pago(self) -> dict:
        """Carga los factores de pago (cross) si no están cargados"""
        if self._factores_pago is None:
            try:
                repos = get_repos("cross")  # Factores de pago son cross
                factores_pago_repo = repos.get("factores_pago")
                if factores_pago_repo:
                    self._factores_pago = factores_pago_repo.get_factores_pago()
                else:
                    self._factores_pago = {}
            except Exception as e:
                print(f"Error al cargar factores de pago: {e}")
                self._factores_pago = {}
        return self._factores_pago

    def get_parametros_calculados(
        self,
        parametros_entrada: Dict[str, Any],
        parametros_almacenados: Dict[str, Any],
        tasas_interes_data: Dict[str, Any],
        producto: Producto,
        cobertura: str = None,
    ) -> Dict[str, Any]:
        """
        Calcula todos los parámetros calculados de una vez

        Args:
            parametros_entrada: Parámetros de entrada del usuario
            parametros_almacenados: Parámetros almacenados de la cobertura
            tasas_interes_data: Datos de tasas de interés (cargados externamente)
            producto: Tipo de producto (Producto.ENDOSOS, etc.)
            cobertura: Nombre de la cobertura (opcional)

        Returns:
            Diccionario con todos los parámetros calculados
        """
        parametros_calculados = {}

        # Obtener parámetros básicos
        prima = parametros_almacenados.get("prima_asignada")
        gasto_adquisicion = parametros_almacenados.get("gasto_adquisicion")
        gasto_mantenimiento = parametros_almacenados.get("gasto_mantenimiento")
        moce = parametros_almacenados.get("moce")
        inflacion_anual = parametros_almacenados.get("inflacion_anual")
        tasa_costo_capital_tir = parametros_almacenados.get("tasa_costo_capital_tir")
        margen_solvencia = parametros_almacenados.get("margen_solvencia")
        fondo_garantia = parametros_almacenados.get("fondo_garantia")
        factor_ajuste = parametros_almacenados.get("factor_ajuste")
        reserva_endosos = parametros_almacenados.get("reserva_endosos")

        # Obtener parámetros de entrada
        periodo_vigencia = parametros_entrada.get("periodo_vigencia")
        periodo_pago_primas = parametros_entrada.get("periodo_pago_primas")
        frecuencia_pago_str = parametros_entrada.get(
            "frecuencia_pago_primas", "MENSUAL"
        )

        # Determinar si es cobertura adicional
        # Para endosos: fallecimiento = principal (False), itp = adicional (True)
        if producto == Producto.ENDOSOS:
            cobertura_adicional = cobertura == "itp"  # Solo ITP es adicional
        else:
            cobertura_adicional = cobertura is not None

        # 1. Gastos
        if prima > 0:
            parametros_calculados["adquisicion_fijo_poliza"] = (
                self.calcular_adquisicion_fijo_poliza(gasto_adquisicion, prima)
            )
        else:
            parametros_calculados["adquisicion_fijo_poliza"] = 0

        parametros_calculados["calcular_mantenimiento_poliza"] = (
            self.calcular_mantenimiento_poliza(gasto_mantenimiento, prima)
        )

        # 2. Tasas
        parametros_calculados["tir_mensual"] = self.calcular_tir_mensual(
            producto, cobertura_adicional, moce
        )

        parametros_calculados["inflacion_mensual"] = self.calcular_inflacion_mensual(
            inflacion_anual
        )

        parametros_calculados["tasa_interes_anual"] = self.calcular_tasa_interes_anual(
            tasas_interes_data, periodo_vigencia
        )

        parametros_calculados["tasa_interes_mensual"] = (
            self.calcular_tasa_interes_mensual(
                producto,
                cobertura_adicional,
                parametros_calculados["tasa_interes_anual"],
            )
        )

        parametros_calculados["tasa_inversion"] = self.calcular_tasa_inversion(
            tasas_interes_data, periodo_pago_primas
        )

        parametros_calculados["tasa_costo_capital_mes"] = (
            self.calcular_tasa_costo_capital_mes(tasa_costo_capital_tir)
        )

        # 3. Reservas
        parametros_calculados["reserva"] = self.calcular_reserva(
            producto,
            cobertura_adicional,
            margen_solvencia,
            fondo_garantia,
            factor_ajuste,
            reserva_endosos,
        )

        # 4. Factores de pago (cross - cargados internamente)
        try:
            frecuencia_pago = FrecuenciaPago(frecuencia_pago_str)
        except ValueError:
            frecuencia_pago = FrecuenciaPago.MENSUAL

        factores_pago = self._cargar_factores_pago()

        parametros_calculados["factor_pago"] = self.calcular_factor_pago(
            frecuencia_pago, factores_pago
        )

        return parametros_calculados

    # Métodos individuales (mantener para compatibilidad)
    def calcular_adquisicion_fijo_poliza(
        self, gasto_adquisicion: float, prima: float
    ) -> float:
        return self.parametros_calculados.calcular_adquisicion_fijo_poliza(
            gasto_adquisicion, prima
        )

    def calcular_mantenimiento_poliza(
        self, gasto_mantenimiento: float, prima: float
    ) -> float:
        return self.parametros_calculados.calcular_mantenimiento_poliza(
            gasto_mantenimiento, prima
        )

    def calcular_tir_mensual(
        self, producto: Producto, coberturas: bool, moce: float
    ) -> float:
        return self.parametros_calculados.calcular_tir_mensual(
            producto, coberturas, moce
        )

    def calcular_inflacion_mensual(self, inflacion_anual: float) -> float:
        return self.parametros_calculados.calcular_inflacion_mensual(inflacion_anual)

    def calcular_tasa_interes_anual(
        self, tasas_interes_data: dict, periodo_vigencia: int
    ) -> float:
        return self.parametros_calculados.calcular_tasa_interes_anual(
            tasas_interes_data, periodo_vigencia
        )

    def calcular_tasa_interes_mensual(
        self, producto: Producto, coberturas: bool, tasa_interes_anual: float
    ) -> float:
        return self.parametros_calculados.calcular_tasa_interes_mensual(
            producto, coberturas, tasa_interes_anual
        )

    def calcular_tasa_inversion(
        self, tasas_interes_data: dict, periodo_pago_primas: int
    ) -> float:
        return self.parametros_calculados.calcular_tasa_inversion(
            tasas_interes_data, periodo_pago_primas
        )

    def calcular_tasa_costo_capital_mes(self, tasa_costo_capital_tir: float) -> float:
        return self.parametros_calculados.calcular_tasa_costo_capital_mes(
            tasa_costo_capital_tir
        )

    def calcular_reserva(
        self,
        producto: Producto,
        coberturas: bool,
        margen_solvencia: float,
        fondo_garantia: float,
        factor_ajuste: float,
        reserva_endosos: float,
    ) -> float:
        return self.parametros_calculados.calcular_reserva(
            producto,
            coberturas,
            margen_solvencia,
            fondo_garantia,
            factor_ajuste,
            reserva_endosos,
        )

    def calcular_factor_pago(
        self, frecuencia_pago_primas: FrecuenciaPago, factores_pago: dict
    ) -> float:
        return self.parametros_calculados.calcular_factor_pago(
            frecuencia_pago_primas, factores_pago
        )

    def calcular_prima_para_redondeo(self, prima: float, factor_pago: float) -> float:
        return self.parametros_calculados.calcular_prima_para_redondeo(
            prima, factor_pago
        )

    def calcular_tasa_frecuencia_seleccionada(
        self, prima_para_redondeo: float, suma_asegurada: float
    ) -> float:
        return self.parametros_calculados.calcular_tasa_frecuencia_seleccionada(
            prima_para_redondeo, suma_asegurada
        )

    def calcular_factor_ajuste(self, producto: Producto) -> float:
        return self.parametros_calculados.calcular_factor_ajuste(producto)
