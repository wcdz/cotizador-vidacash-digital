from src.models.services.expuestos_mes_service import ExpuestosMesService
from src.models.services.gastos_service import GastosService
from src.models.services.flujo_resultado_service import FlujoResultadoService
from src.models.services.reserva_service import ReservaService
from src.models.services.margen_solvencia_service import MargenSolvenciaService
from src.common.producto import Producto
from typing import Dict, Any


class CalculoActuarialService:
    """Servicio que orquesta los cálculos actuariales"""

    def __init__(
        self,
        parametros_entrada: Dict[str, Any],
        parametros_almacenados: Dict[str, Any],
        parametros_calculados: Dict[str, Any],
        producto: Producto,
        sexo: str,
        fumador: bool,
        cobertura: str,
    ):
        """
        Inicializa el servicio de cálculo actuarial

        Args:
            parametros_entrada: Parámetros de entrada del usuario
            parametros_almacenados: Parámetros almacenados de la cobertura
            parametros_calculados: Parámetros calculados
            producto: Tipo de producto
            cobertura: Cobertura específica (ej: "fallecimiento", "itp")
        """
        self.parametros_entrada = parametros_entrada
        self.parametros_almacenados = parametros_almacenados
        self.parametros_calculados = parametros_calculados
        self.producto = producto
        self.cobertura = cobertura
        self.sexo = sexo
        self.fumador = fumador

        # Procesar fallecimiento e ITP
        if cobertura in ["fallecimiento", "itp"]:
            # Extraer valores específicos para el ExpuestosMesService
            periodo_vigencia = parametros_entrada.get("periodo_vigencia", 1)
            edad_actuarial = parametros_entrada.get("edad_actuarial", 1)
            suma_asegurada = parametros_entrada.get("suma_asegurada", 1)
            porcentaje_devolucion = parametros_entrada.get("porcentaje_devolucion")
            self.periodo_pago_primas = parametros_entrada.get("periodo_pago_primas", 1)
            self.frecuencia_pago_primas = parametros_entrada.get(
                "frecuencia_pago_primas", "MENSUAL"
            )

            # Extraer valores de prima desde la cobertura específica
            cobertura_params = parametros_almacenados.get("coberturas", {}).get(
                cobertura, {}
            )
            self.prima = cobertura_params.get("prima_asignada")
            self.fraccionamiento_primas = cobertura_params.get("fraccionamiento_primas")

            # Extraer mantenimiento_poliza desde parámetros calculados
            cobertura_calculados = parametros_calculados.get("coberturas", {}).get(
                cobertura, {}
            )
            mantenimiento_poliza = cobertura_calculados.get(
                "calcular_mantenimiento_poliza", 0
            )
            moneda = cobertura_params.get("moneda")
            valor_dolar = cobertura_params.get("valor_dolar")
            valor_soles = cobertura_params.get("valor_soles")
            self.tiene_asistencia = cobertura_params.get("tiene_asistencia")
            self.costo_mensual_asistencia_funeraria = cobertura_params.get(
                "costo_mensual_asistencia_funeraria"
            )
            inflacion_mensual = cobertura_calculados.get("inflacion_mensual")
            self.gasto_adquisicion = cobertura_params.get("gasto_adquisicion")
            self.comision = cobertura_params.get("comision")
            self.tasa_interes_mensual = cobertura_calculados.get("tasa_interes_mensual")
            self.margen_solvencia = cobertura_params.get("margen_solvencia")
            self.tir_mensual = cobertura_calculados.get("tir_mensual")
            self.reserva = cobertura_calculados.get("reserva")
            self.tasa_inversion = cobertura_calculados.get("tasa_inversion")
            self.impuesto_renta = cobertura_params.get("impuesto_renta")
            self.tasa_costo_capital_mes = cobertura_calculados.get(
                "tasa_costo_capital_mes"
            )

            self.expuestos_mes_service = ExpuestosMesService(
                producto=producto,
                periodo_vigencia=periodo_vigencia,
                edad_actuarial=edad_actuarial,
                sexo=sexo,
                fumador=fumador,
                cobertura=cobertura,
            )
            self.gastos_service = GastosService(
                producto=producto,
                cobertura=cobertura,
                periodo_pago_primas=self.periodo_pago_primas,
                frecuencia_pago_primas=self.frecuencia_pago_primas,
                prima=self.prima,
                fraccionamiento_primas=self.fraccionamiento_primas,
                mantenimiento_poliza=mantenimiento_poliza,
                moneda=moneda,
                valor_dolar=valor_dolar,
                valor_soles=valor_soles,
                tiene_asistencia=self.tiene_asistencia,
                costo_mensual_asistencia_funeraria=self.costo_mensual_asistencia_funeraria,
                inflacion_mensual=inflacion_mensual,
                periodo_vigencia=periodo_vigencia,
            )
            self.flujo_resultado_service = FlujoResultadoService(
                producto=producto,
                cobertura=cobertura,
                suma_asegurada=suma_asegurada,
                edad_actuarial=edad_actuarial,
                periodo_vigencia=periodo_vigencia,
                prima=self.prima,
                fraccionamiento_primas=self.fraccionamiento_primas,
                porcentaje_devolucion=porcentaje_devolucion,
            )
            self.reserva_service = ReservaService(
                producto=producto,
                cobertura=cobertura,
                periodo_vigencia=periodo_vigencia,
                prima=self.prima,
                fraccionamiento_primas=self.fraccionamiento_primas,
                porcentaje_devolucion=porcentaje_devolucion,
            )
            self.margen_solvencia_service = MargenSolvenciaService()
        else:
            self.expuestos_mes_service = None
            self.gastos_service = None

    def execute(self):
        """Ejecuta todos los cálculos actuariales"""
        if self.expuestos_mes_service is not None:
            expuestos_mes = self.expuestos_mes_service.calcular_expuestos_mes()
            vivos_inicio = [expuestos_mes[mes]["vivos_inicio"] for mes in expuestos_mes]
            fallecidos = [expuestos_mes[mes]["fallecidos"] for mes in expuestos_mes]
            caducados = [expuestos_mes[mes]["caducados"] for mes in expuestos_mes]
            primas_recurrentes = (
                self.flujo_resultado_service.calcular_primas_recurrentes(
                    vivos_inicio,
                    self.periodo_pago_primas,
                    self.frecuencia_pago_primas,
                    self.prima,
                    self.fraccionamiento_primas,
                )
            )
            gastos = self.gastos_service.calcular_gastos(
                vivos_inicio, primas_recurrentes
            )
            gastos_mantenimiento_total = gastos["gastos_mantenimiento_total"]
            siniestros = self.flujo_resultado_service.calcular_siniestros(
                fallecidos, vivos_inicio
            )
            rescate = self.reserva_service.calcular_rescate()
            rescate_ajuste_devolucion = self.flujo_resultado_service.calcular_rescate(
                caducados, rescate
            )
            gastos_mantenimiento = (
                self.flujo_resultado_service.calcular_gastos_mantenimiento(
                    gastos_mantenimiento_total
                )
            )
            gastos_adquisicion = (
                self.flujo_resultado_service.calcular_gastos_adquisicion(
                    self.gasto_adquisicion
                )
            )

            comision = self.flujo_resultado_service.calcular_comision(
                primas_recurrentes,
                vivos_inicio,
                self.frecuencia_pago_primas,
                self.tiene_asistencia,
                self.costo_mensual_asistencia_funeraria,
                self.comision,
            )

            flujo_pasivo = self.reserva_service.calcular_flujo_pasivo(
                primas_recurrentes,
                siniestros,
                rescate_ajuste_devolucion,
                gastos_mantenimiento,
                gastos_adquisicion,
                comision,
            )

            saldo_reserva = self.reserva_service.calcular_saldo_reserva(
                vivos_inicio,
                rescate,
                flujo_pasivo,
                self.tasa_interes_mensual,
            )

            moce = self.reserva_service.calcular_moce(
                self.tir_mensual,
                self.tasa_interes_mensual,
                self.margen_solvencia,
                saldo_reserva,
            )

            moce_saldo_reserva = self.reserva_service.calcular_moce_saldo_reserva(
                saldo_reserva, moce
            )

            reserva_fin_año = self.margen_solvencia_service.calcular_reserva_fin_año(
                moce_saldo_reserva
            )

            margen_solvencia = self.margen_solvencia_service.calcular_margen_solvencia(
                reserva_fin_año, self.reserva
            )

            varianza_margen_solvencia = (
                self.margen_solvencia_service.calcular_varianza_margen_solvencia(
                    margen_solvencia
                )
            )

            ingreso_inversiones = (
                self.margen_solvencia_service.calcular_ingreso_inversiones(
                    reserva_fin_año, self.tasa_inversion
                )
            )

            ingreso_inversiones_margen_solvencia = self.margen_solvencia_service.calcular_ingreso_inversiones_margen_solvencia(
                margen_solvencia, self.tasa_inversion
            )

            ingreso_total_inversiones = (
                self.margen_solvencia_service.calcular_ingreso_total_inversiones(
                    ingreso_inversiones, ingreso_inversiones_margen_solvencia
                )
            )

            varianza_moce = self.reserva_service.calcular_varianza_moce(moce)

            varianza_reserva = self.reserva_service.calcular_varianza_reserva(
                saldo_reserva
            )

            variacion_reserva = self.flujo_resultado_service.calcular_variacion_reserva(
                varianza_reserva, varianza_moce
            )

            utilidad_pre_pi_ms = (
                self.flujo_resultado_service.calcular_utilidad_pre_pi_ms(
                    primas_recurrentes,
                    comision,
                    gastos_mantenimiento,
                    gastos_adquisicion,
                    siniestros,
                    rescate_ajuste_devolucion,
                    variacion_reserva,
                )
            )

            variacion_margen_solvencia = (
                self.flujo_resultado_service.calcular_variacion_margen_solvencia(
                    varianza_margen_solvencia
                )
            )

            IR = self.flujo_resultado_service.calcular_IR(
                utilidad_pre_pi_ms, self.impuesto_renta
            )

            producto_inversion = (
                self.flujo_resultado_service.calcular_producto_inversion(
                    ingreso_total_inversiones
                )
            )

            flujo_resultado = self.flujo_resultado_service.calcular_flujo_resultado(
                utilidad_pre_pi_ms,
                variacion_margen_solvencia,
                IR,
                producto_inversion,
            )

            vna_resultado = self.flujo_resultado_service.calcular_vna_resultado(
                flujo_resultado, self.tasa_costo_capital_mes
            )

            print(vna_resultado)

            return vna_resultado
        else:
            print(
                f"Cobertura '{self.cobertura}' no soportada para cálculos actuariales"
            )
            return {}, {}
