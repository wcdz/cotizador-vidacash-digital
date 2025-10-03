from src.helpers.redondeo_mensual import redondeo_mensual


class MargenSolvenciaDomain:

    def calcular_margen_solvencia(self, reserva_fin_año, reserva):
        return [rfa * reserva for rfa in reserva_fin_año]

    def calcular_varianza_margen_solvencia(self, margen_solvencia):
        varianza_margen_solvencia = [margen_solvencia[0]] + [
            actual - anterior
            for anterior, actual in zip(margen_solvencia, margen_solvencia[1:])
        ]
        varianza_margen_solvencia.append(-margen_solvencia[-1])
        return varianza_margen_solvencia

    def calcular_ingreso_inversiones(self, reserva_fin_año, tasa_inversion):
        return [rfa * redondeo_mensual(tasa_inversion) for rfa in reserva_fin_año]

    def calcular_ingreso_inversiones_margen_solvencia(
        self, margen_solvencia, tasa_inversion
    ):
        return [ms * redondeo_mensual(tasa_inversion) for ms in margen_solvencia]

    def calcular_ingreso_total_inversiones(
        self, ingreso_inversiones, ingreso_inversiones_margen_solvencia
    ):
        return [
            ii + ii_ms
            for ii, ii_ms in zip(
                ingreso_inversiones, ingreso_inversiones_margen_solvencia
            )
        ]
