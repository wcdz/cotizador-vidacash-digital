from src.models.domain.reserva_domain import ReservaDomain
from src.common.producto import Producto
from src.infrastructure.repositories import get_repos


class ReservaService:

    def __init__(
        self,
        producto: Producto,
        cobertura: str,
        periodo_vigencia: int,
        prima: float,
        fraccionamiento_primas: float,
        porcentaje_devolucion: float,
    ):
        self.producto = producto
        self.cobertura = cobertura
        self.periodo_vigencia = periodo_vigencia
        self.prima = prima
        self.fraccionamiento_primas = fraccionamiento_primas
        self.porcentaje_devolucion = porcentaje_devolucion
        
        repos = get_repos(producto=self.producto.value, cobertura=self.cobertura)
        self.matriz_devolucion = repos[
            "devolucion"
        ].get_devolucion_by_producto_and_cobertura(
            producto=self.producto.value, cobertura=self.cobertura
        )
        
        self.reserva = ReservaDomain(
            periodo_vigencia=periodo_vigencia,
            matriz_devolucion=self.matriz_devolucion,
            prima=prima,
            fraccionamiento_primas=fraccionamiento_primas,
            porcentaje_devolucion=porcentaje_devolucion,
        )

    def calcular_rescate(self):
        return self.reserva.calcular_rescate()
