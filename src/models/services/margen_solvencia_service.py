from src.models.domain.margen_solvencia_domain import MargenSolvenciaDomain


class MargenSolvenciaService:

    def __init__(self):
        self.margen_solvencia_domain = MargenSolvenciaDomain()

    def calcular_reserva_fin_año(self, moce_saldo_reserva):
        return moce_saldo_reserva

    def calcular_margen_solvencia(self, reserva_fin_año, reserva):
        return self.margen_solvencia_domain.calcular_margen_solvencia(
            reserva_fin_año, reserva
        )

    def calcular_varianza_margen_solvencia(self, margen_solvencia):
        return self.margen_solvencia_domain.calcular_varianza_margen_solvencia(
            margen_solvencia
        )

    def calcular_ingreso_inversiones(self, reserva_fin_año, tasa_inversion):
        return self.margen_solvencia_domain.calcular_ingreso_inversiones(
            reserva_fin_año, tasa_inversion
        )

    def calcular_ingreso_inversiones_margen_solvencia(
        self, margen_solvencia, tasa_inversion
    ):
        return (
            self.margen_solvencia_domain.calcular_ingreso_inversiones_margen_solvencia(
                margen_solvencia, tasa_inversion
            )
        )

    def calcular_ingreso_total_inversiones(
        self, ingreso_inversiones, ingreso_inversiones_margen_solvencia
    ):
        return self.margen_solvencia_domain.calcular_ingreso_total_inversiones(
            ingreso_inversiones, ingreso_inversiones_margen_solvencia
        )
