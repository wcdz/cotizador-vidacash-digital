from src.models.domain.flujo_resultado import FlujoResultado


class FlujoResultadoService:
    
    def __init__(self):
        self.flujo_resultado = FlujoResultado()

    def calcular_primas_recurrentes(
        self,
        vivos_inicio: float,
        periodo_pago_primas: float,
        frecuencia_pago_primas: str,
        prima: float,
        fraccionamiento_primas: float,
    ):
        return self.flujo_resultado.calcular_primas_recurrentes(
            vivos_inicio,
            periodo_pago_primas,
            frecuencia_pago_primas,
            prima,
            fraccionamiento_primas,
        )
