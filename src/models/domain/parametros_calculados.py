from dataclasses import dataclass, field
from src.common.constans import TASA_MENSUALIZACION, FACTOR_AJUSTE
from src.helpers.tasa_interes_reserva import tasa_interes_reserva
from src.common.frecuencia_pago import FrecuenciaPago
from typing import Dict, Any
from src.common.producto import Producto


class ParametrosCalculados:

    def calcular_adquisicion_fijo_poliza(
        self, gasto_adquisicion: float, prima: float
    ) -> float:
        """Calcula el gasto de adquisición fijo por póliza"""
        return gasto_adquisicion / prima

    def calcular_mantenimiento_poliza(
        self, gasto_mantenimiento: float, prima: float
    ) -> float:
        """Calcula el gasto de mantenimiento por póliza"""
        return gasto_mantenimiento / prima

    def calcular_tir_mensual(
        self, producto: Producto, coberturas: bool, moce: float
    ) -> float:
        """Calcula la TIR mensual"""
        exponente = (
            1 / 12
            if (producto == Producto.ENDOSOS and coberturas) or (producto == Producto.VIDA_CASH_PLUS and coberturas)
            else TASA_MENSUALIZACION
        )
        return (1 + moce) ** exponente - 1

    def calcular_inflacion_mensual(self, inflacion_anual: float) -> float:
        """Calcula la inflación mensual a partir de la anual"""
        return (1 + inflacion_anual) ** (TASA_MENSUALIZACION) - 1

    def calcular_reserva(
        self,
        producto: Producto,
        coberturas: bool,
        margen_solvencia: float,
        fondo_garantia: float,
        factor_ajuste: float,
        reserva_endosos: float,
    ) -> float:
        """Calcula la reserva"""
        match (producto, bool(coberturas)):
            case (Producto.RUMBO, _):
                return margen_solvencia * (1 + fondo_garantia) * factor_ajuste
            case (Producto.ENDOSOS, True):
                return margen_solvencia * (1 + fondo_garantia)
            case (Producto.ENDOSOS, False):
                return reserva_endosos
            case (Producto.VIDA_CASH_PLUS, True):
                return margen_solvencia * (1 + fondo_garantia)
            case (Producto.VIDA_CASH_PLUS, False):
                return reserva_endosos
            case _:
                raise ValueError(f"Tipo de producto no válido: {producto}")

    def calcular_tasa_interes_anual(
        self, tasas_interes_data: dict, periodo_vigencia: int
    ) -> float:
        """Calcula la tasa de interés anual basada en la tabla de tasas de interés"""
        try:
            tasa_interes_anual = tasa_interes_reserva(tasas_interes_data)[
                str(periodo_vigencia)
            ]
            tasa_reserva = tasa_interes_anual["tasa_reserva"]
            return tasa_reserva
        except KeyError:
            raise ValueError(
                f"No se encontró una tasa para el periodo {periodo_vigencia}"
            )

    def calcular_tasa_interes_mensual(
        self,
        producto: Producto,
        coberturas: bool,
        tasa_interes_anual: float,
    ) -> float:
        """Calcula la tasa de interés mensual"""
        tasa_interes_anual = tasa_interes_anual / 100
        if (producto == Producto.ENDOSOS and coberturas) or (producto == Producto.VIDA_CASH_PLUS and coberturas):
            return (1 + tasa_interes_anual) ** (1 / 12) - 1
        else:
            return (1 + tasa_interes_anual) ** (TASA_MENSUALIZACION) - 1

    def calcular_tasa_inversion(
        self, tasas_interes_data: dict, periodo_pago_primas: int
    ) -> float:
        """Calcula la tasa de inversión"""
        # Implementar fórmula específica según requerimiento
        tasa_interes_anual = tasa_interes_reserva(tasas_interes_data)[
            str(periodo_pago_primas)
        ]
        tasa_inversion = tasa_interes_anual["tasa_inversion"] / 100
        return tasa_inversion

    def calcular_tasa_costo_capital_mes(self, tasa_costo_capital_tir: float) -> float:
        """Calcula la tasa de costo capital mensual"""
        return (1 + tasa_costo_capital_tir) ** (1 / 12) - 1

    def calcular_factor_pago(
        self, frecuencia_pago_primas: FrecuenciaPago, factores_pago: dict
    ) -> float:
        """
        Calcula el factor de pago según la frecuencia y el diccionario de factores.
        """
        clave = frecuencia_pago_primas.value.lower()  # "anual", "semestral", etc.
        return float(factores_pago.get(clave, 1.0))  # 1.0 por defecto si no existe

    def calcular_prima_para_redondeo(prima: float, factor_pago: float) -> float:
        """Calcula la prima para redondeo"""
        return prima / factor_pago * factor_pago

    def calcular_tasa_frecuencia_seleccionada(
        self, prima_para_redondeo: float, suma_asegurada: float
    ) -> float:
        """Calcula la tasa de frecuencia seleccionada"""
        return prima_para_redondeo / suma_asegurada

    def calcular_factor_ajuste(self, producto: Producto) -> float:
        """Calcula el factor de ajuste según el tipo de producto"""
        return FACTOR_AJUSTE if producto == Producto.RUMBO else 0.0

    def calcular_tabla_devolucion(
        self, periodo_vigencia: int, porcentaje_devolucion: float, devolucion: list
    ) -> list:
        """Calcula la tabla de devoluciones"""
        print(f"🔍 Debug tabla devolución:")
        print(f"  - Periodo vigencia: {periodo_vigencia}")
        print(f"  - Porcentaje devolución: {porcentaje_devolucion}")
        print(f"  - Datos devolución: {len(devolucion)} elementos")
        print(f"  - Slice a procesar: devolucion[:{periodo_vigencia - 1}]")
        
        if not devolucion:
            print("⚠️ Lista de devolución vacía, devolviendo solo porcentaje")
            return [porcentaje_devolucion]
        
        # Procesar elementos hasta periodo_vigencia - 1
        elementos_procesados = []
        for i, x in enumerate(devolucion[: periodo_vigencia - 1]):
            plazo_pago = x.get("plazo_pago_primas", {})
            valor_periodo = plazo_pago.get(str(periodo_vigencia), 0)
            resultado = valor_periodo * (porcentaje_devolucion / 100)
            elementos_procesados.append(resultado)
            print(f"  - Elemento {i}: plazo_pago_primas[{periodo_vigencia}] = {valor_periodo}, resultado = {resultado}")
        
        # Agregar porcentaje_devolucion al final
        resultado_final = elementos_procesados + [porcentaje_devolucion]
        print(f"  - Resultado final: {resultado_final}")
        
        return resultado_final
