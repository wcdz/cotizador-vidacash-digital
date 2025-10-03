from src.utils.anios_meses import anios_meses
from typing import List
import numpy as np
from src.helpers.margen_reserva import margen_reserva


class ReservaDomain:

    def __init__(
        self,
        periodo_vigencia: int,
        matriz_devolucion: dict,
        prima: float,
        fraccionamiento_primas: float,
        porcentaje_devolucion: float,
    ):
        self.periodo_vigencia = periodo_vigencia
        self.matriz_devolucion = matriz_devolucion
        self.prima = prima
        self.fraccionamiento_primas = fraccionamiento_primas
        self.primas_pagadas = self.calcular_primas_pagadas(
            self.periodo_vigencia, self.prima, self.fraccionamiento_primas
        )
        self.porcentaje_devolucion_anual = self.calcular_porcentaje_devolucion_anual(
            self.periodo_vigencia, self.matriz_devolucion
        )
        self.porcentaje_devolucion_mensual = (
            self.calcular_porcentaje_devolucion_mensual(self.periodo_vigencia)
        )
        self.porcentaje_devolucion = porcentaje_devolucion / 100

    def calcular_rescate(self):
        primas_pagadas = self.primas_pagadas
        porcentaje_devolucion_mensual = self.porcentaje_devolucion_mensual

        rescates = []
        for i in range(len(primas_pagadas)):
            año_poliza = (i // 12) + 1
            mes_poliza = i + 1
            _porcentaje_devolucion = self.porcentaje_devolucion

            if año_poliza <= self.periodo_vigencia:
                rescate = (
                    self.prima
                    * _porcentaje_devolucion
                    * mes_poliza
                    * porcentaje_devolucion_mensual[i]
                )
            else:
                rescate = 0

            rescates.append(rescate)

        return rescates

    def calcular_primas_pagadas(
        self, periodo_vigencia: int, prima: float, fraccionamiento_primas: float
    ):
        meses_total_poliza = periodo_vigencia * 12
        primas_pagadas = []

        for mes_poliza in range(1, meses_total_poliza + 1):
            anio_poliza = (mes_poliza - 1) // 12 + 1

            if anio_poliza > periodo_vigencia:
                primas_pagadas.append(0.0)
            else:
                primas_pagadas.append(prima * fraccionamiento_primas)

        return primas_pagadas

    def calcular_porcentaje_devolucion_mensual(self, periodo_vigencia: int):
        porcentaje_devolucion_anual = self.porcentaje_devolucion_anual
        total_meses = anios_meses(periodo_vigencia)
        porcentaje_devolucion_mensual = []

        for i in range(total_meses):
            mes_poliza = i + 1
            anio_poliza = (i // 12) + 1
            mes_del_anio = (i % 12) + 1

            if mes_poliza > total_meses:
                porcentaje_devolucion_mensual.append(0.0)
            elif (
                anio_poliza == periodo_vigencia
                and (mes_poliza / mes_del_anio) == periodo_vigencia
            ):
                porcentaje_devolucion_mensual.append(1.0)
            else:
                porcentaje = (
                    porcentaje_devolucion_anual[anio_poliza - 1]
                    if anio_poliza - 1 < len(porcentaje_devolucion_anual)
                    else 0.0
                )
                porcentaje_devolucion_mensual.append(porcentaje)
        return porcentaje_devolucion_mensual

    def calcular_porcentaje_devolucion_anual(
        self, periodo_vigencia: float, matriz_devolucion: dict
    ):
        anios = periodo_vigencia
        porcentaje_devolucion_anual = []

        # Iteramos desde el año 1 hasta el último año
        for anio_poliza in range(1, anios + 1):
            # Buscamos la fila correspondiente al año de póliza actual
            fila = next(
                (
                    item
                    for item in matriz_devolucion
                    if item["año_poliza"] == anio_poliza
                ),
                None,
            )

            if not fila:
                porcentaje_devolucion_anual.append(0)
                continue

            plazo_primas = fila.get("plazo_pago_primas", {})
            porcentaje = plazo_primas.get(str(periodo_vigencia), 0.0) / 100

            porcentaje_devolucion_anual.append(porcentaje)

        return porcentaje_devolucion_anual

    def calcular_rescate_ajuste_devolucion(
        self, caducados: List[float], rescates: List[float]
    ):
        return [rescate * caducado for rescate, caducado in zip(rescates, caducados)]

    def calcular_flujo_pasivo(
        self,
        primas_recurrentes: List[float],
        siniestros: List[float],
        rescate_ajuste_devolucion: List[float],
        gastos_mantenimiento: List[float],
        gastos_adquisicion: List[float],
        comision: List[float],
    ):
        flujo_pasivo = []
        for i, (siniestro, rescate, mantenimiento, comision, prima) in enumerate(
            zip(
                siniestros,
                rescate_ajuste_devolucion,
                gastos_mantenimiento,
                comision,
                primas_recurrentes,
            )
        ):
            adquisicion = gastos_adquisicion if i == 0 else 0.0
            flujo = (
                (-siniestro)
                + (-rescate)
                + (-mantenimiento)
                + (-comision)
                + (-adquisicion)
            ) - prima
            flujo_pasivo.append(flujo)
        return flujo_pasivo

    def vna_excel(self, rate: float, cashflows: List[float]) -> float:
        """
        Replica EXACTO la función VNA de Excel:
        - Descuenta a partir del primer flujo como (1+r)^1, no como np.npv
        """
        return sum(cf / (1 + rate) ** (t + 1) for t, cf in enumerate(cashflows))

    def calcular_saldo_reserva(
        self,
        vivos_inicio: List[float],
        rescate: List[float],
        flujo_pasivo: List[float],
        tasa_interes_mensual: float,
    ):
        # print(vivos_inicio) # OK
        # print(rescate) # OK -> Diferencia al 14vo decimal
        # print(flujo_pasivo) # OK
        # print(tasa_interes_mensual) # OK

        resultados = []
        n = len(flujo_pasivo)

        for i in range(n):
            # VNA Excel desde el flujo siguiente (i+1 en adelante)
            vna = self.vna_excel(tasa_interes_mensual, flujo_pasivo[i + 1 :])

            # parte izquierda (flujo actual + VNA)
            valor = flujo_pasivo[i] + vna
            if valor < 0:
                valor = 0

            # parte derecha
            comparador = rescate[i] * vivos_inicio[i]

            resultados.append(max(valor, comparador))

        return resultados

    def calcular_moce(
        self,
        tasa_costo_capital_mensual: float,
        tasa_interes_mensual: float,
        margen_solvencia: float,
        saldo_reserva: List[float],
    ):

        _margen_reserva = margen_reserva(saldo_reserva, margen_solvencia)

        if not _margen_reserva:
            return []

        resultados_moce = []

        for i in range(len(_margen_reserva)):
            flujo_inicial = _margen_reserva[i]
            flujos_futuros = _margen_reserva[i + 1 :]  # del siguiente en adelante

            vna = sum(
                flujo / ((1 + tasa_interes_mensual) ** j)
                for j, flujo in enumerate(flujos_futuros, start=1)
            )

            moce = tasa_costo_capital_mensual * (vna + flujo_inicial)
            resultados_moce.append(moce)

        return resultados_moce

    def calcular_moce_saldo_reserva(
        self, saldo_reserva: List[float], moce: List[float]
    ):
        return [saldo + moce for saldo, moce in zip(saldo_reserva, moce)]

    def calcular_varianza_moce(self, moce: List[float]):
        variaciones = [-moce[0]] + [
            -(curr - prev) for prev, curr in zip(moce, moce[1:])
        ]

        variaciones.append(moce[-1])  # Último elemento positivo
        return variaciones

    def calcular_varianza_reserva(self, saldo_reserva: List[float]):
        variaciones = [-saldo_reserva[0]] + [
            -(curr - prev) for prev, curr in zip(saldo_reserva, saldo_reserva[1:])
        ]
        variaciones.append(saldo_reserva[-1])  # Último elemento positivo

        return variaciones
