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
