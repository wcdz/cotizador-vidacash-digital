from src.models.services.expuestos_mes_service import ExpuestosMesService
from src.common.producto import Producto
from typing import Dict, Any


class CalculoActuarialService:
    """Servicio que orquesta los cálculos actuariales"""

    def __init__(
        self,
        parametros_entrada: Dict[str, Any],
        parametros_almacenados: Dict[str, Any],
        parametros_calculados: Dict[str, Any],
        producto: Producto,
        sexo: str,
        fumador: bool,
        cobertura: str,
    ):
        """
        Inicializa el servicio de cálculo actuarial

        Args:
            parametros_entrada: Parámetros de entrada del usuario
            parametros_almacenados: Parámetros almacenados de la cobertura
            parametros_calculados: Parámetros calculados
            producto: Tipo de producto
            cobertura: Cobertura específica (ej: "fallecimiento", "itp")
        """
        self.parametros_entrada = parametros_entrada
        self.parametros_almacenados = parametros_almacenados
        self.parametros_calculados = parametros_calculados
        self.producto = producto
        self.cobertura = cobertura
        self.sexo = sexo
        self.fumador = fumador
        
        # Procesar fallecimiento e ITP
        if cobertura in ["fallecimiento", "itp"]:
            # Extraer valores específicos para el ExpuestosMesService
            periodo_vigencia = parametros_entrada.get("periodo_vigencia", 1)
            edad_actuarial = parametros_entrada.get("edad_actuarial", 1)
            
            self.expuestos_mes_service = ExpuestosMesService(
                producto=producto,
                periodo_vigencia=periodo_vigencia,
                edad_actuarial=edad_actuarial,
                sexo=sexo,
                fumador=fumador,
                cobertura=cobertura,
            )
        else:
            self.expuestos_mes_service = None

    def execute(self):
        """Ejecuta todos los cálculos actuariales"""
        if self.expuestos_mes_service is not None:
            expuestos_mes = self.expuestos_mes_service.calcular_expuestos_mes()
            return expuestos_mes
        else:
            print(f"Cobertura '{self.cobertura}' no soportada para cálculos actuariales")
            return {}
