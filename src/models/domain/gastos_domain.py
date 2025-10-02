from typing import List


class GastosDomain:

    def calcular_gastos_mantenimiento_prima_co(
        self, primas_recurrentes: List[float], mantenimiento_poliza: float
    ):
        return [prima * mantenimiento_poliza for prima in primas_recurrentes]
