from typing import Dict, Any
from src.utils.frecuencia_meses import frecuencia_meses


class FlujoResultado:

    def calcular_primas_recurrentes(
        self,
        vivos_inicio: float,
        periodo_pago_primas: float,
        frecuencia_pago_primas: str,
        prima: float,
        fraccionamiento_primas: float,
    ):
        frecuencia_meses_valor = frecuencia_meses(frecuencia_pago_primas)

        primas_recurrentes = []
        for i, vivo_inicio in enumerate(vivos_inicio):
            mes_poliza = i + 1
            if mes_poliza / 12 > periodo_pago_primas:
                prima_mes = 0
            else:
                validador_pago = (
                    1 if ((mes_poliza - 1) % frecuencia_meses_valor == 0) else 0
                )
                prima_mes = (
                    validador_pago * prima * vivo_inicio * fraccionamiento_primas
                )

            primas_recurrentes.append(prima_mes)

        return primas_recurrentes
