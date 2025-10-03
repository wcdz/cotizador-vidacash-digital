from typing import Dict, Any
from src.utils.frecuencia_meses import frecuencia_meses
from typing import List


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

    def calcular_siniestros_fallecimiento(
        self, fallecidos: List[float], suma_asegurada: float
    ):
        return [-(suma_asegurada * fallecido) for fallecido in fallecidos]

    def calcular_siniestros_itp(
        self,
        vivos_inicio: List[float],
        suma_asegurada: float,
        edad_actuarial: int,
        periodo_vigencia: int,
        tarifas_reaseguro: List[float],
    ):
        siniestros = []
        for i, vivo_inicio in enumerate(vivos_inicio):
            edad = edad_actuarial + (i // 12)
            anio = i // 12 + 1
            siniestros_ma_anual = tarifas_reaseguro.get(str(edad), {}).get(
                "invalidez_accidental", 0
            )
            siniestros_ma_mensual = (
                1 - (1 - siniestros_ma_anual / 1000) ** (1 / 12)
            ) * 1000
            factor_siniestro = (
                0
                if anio > periodo_vigencia
                else vivo_inicio * siniestros_ma_mensual / 1000
            )

            siniestros.append(-suma_asegurada * factor_siniestro)

        return siniestros
