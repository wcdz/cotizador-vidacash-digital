from typing import List


class GastosDomain:

    def calcular_gastos_mantenimiento_prima_co(
        self, primas_recurrentes: List[float], mantenimiento_poliza: float
    ):
        return [prima * mantenimiento_poliza for prima in primas_recurrentes]

    def calcular_gastos_mantenimiento_moneda_poliza(
        self,
        moneda: str,
        valor_dolar: float,
        valor_soles: float,
        tiene_asistencia: bool,
        costo_mensual_asistencia_funeraria: float,
    ):
        if moneda.lower() == "dolar":
            gasto_base = valor_dolar
        else:
            gasto_base = valor_soles

        gasto_total = gasto_base + (
            costo_mensual_asistencia_funeraria if tiene_asistencia else 0
        )

        return gasto_total

    def calcular_gastos_mantenimiento_fijo_poliza_anual(
        self, vivos_inicio: List[float], gastos_mantenimiento_moneda_poliza: float
    ):
        return [
            gastos_mantenimiento_moneda_poliza * vivo_inicio
            for vivo_inicio in vivos_inicio
        ]

    def calcular_factor_inflacion(
        self,
        gastos_mantenimiento_prima_co: List[float],
        gastos_mantenimiento_fijo_poliza_anual: List[float],
        inflacion_mensual: float,
    ):
        factores_inflacion = []

        for i in range(len(gastos_mantenimiento_prima_co)):
            gasto_mantenimiento_prima_co = gastos_mantenimiento_prima_co[i]
            gasto_mantenimiento_fijo_poliza_anual = (
                gastos_mantenimiento_fijo_poliza_anual[i]
            )
            mes = i + 1

            if (
                gasto_mantenimiento_prima_co + gasto_mantenimiento_fijo_poliza_anual
                == 0
            ):
                factor = 0
            else:
                factor = (1 + inflacion_mensual) ** (mes - 1)

            factores_inflacion.append(factor)

        return factores_inflacion

    def calcular_gastos_mantenimiento_total(
        self,
        gastos_mantenimiento_prima_co: List[float],
        gastos_mantenimiento_fijo_poliza_anual: List[float],
        factor_inflacion: List[float],
        periodo_vigencia: float,
    ):
        gasto_mantenimiento_total = []

        for i in range(len(gastos_mantenimiento_prima_co)):
            gasto_mantenimiento_prima_co = gastos_mantenimiento_prima_co[i]
            gasto_mantenimiento_fijo_poliza_anual = (
                gastos_mantenimiento_fijo_poliza_anual[i]
            )
            anio = i // 12 + 1

            if anio > periodo_vigencia:
                gasto = 0
            else:
                gasto = (
                    gasto_mantenimiento_prima_co + gasto_mantenimiento_fijo_poliza_anual
                ) * factor_inflacion[i]

            gasto_mantenimiento_total.append(gasto)

        return gasto_mantenimiento_total
