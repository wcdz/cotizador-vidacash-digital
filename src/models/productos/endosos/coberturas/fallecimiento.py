"""
Módulo específico para la cobertura de fallecimiento
"""

from typing import Dict, Any
import math
from src.infrastructure.repositories import get_repos
from src.models.services.parametros_calculados_service import (
    ParametrosCalculadosService,
)
from src.models.services.calculo_actuarial_service import CalculoActuarialService
from src.common.producto import Producto
from src.common.frecuencia_pago import FrecuenciaPago


class FallecimientoCobertura:
    """Clase específica para manejar la cobertura de fallecimiento"""

    def __init__(self):
        self.producto = "endosos"
        self.cobertura = "fallecimiento"
        self.cobertura_adicional = False  # Referencia a ITP
        self.parametros = {}
        self.parametros_calculados_service = ParametrosCalculadosService()

    def cargar_parametros(self) -> Dict[str, Any]:
        """
        Carga los parámetros específicos para la cobertura de fallecimiento

        Returns:
            Diccionario con los parámetros de fallecimiento
        """
        try:
            # Obtener repositorios específicos para fallecimiento
            repos = get_repos(self.producto, self.cobertura)

            # Obtener el repositorio de parámetros
            parametros_repo = repos.get("parametros")

            if parametros_repo is None:
                print(
                    f"Error: No se encontró el repositorio de parámetros para {self.producto}/{self.cobertura}"
                )
                return {}

            # Cargar parámetros específicos de fallecimiento
            parametros = parametros_repo.get_parametros_by_producto_and_cobertura(
                self.producto, self.cobertura
            )

            self.parametros = parametros
            print(f"Parámetros de fallecimiento cargados: {len(parametros)} parámetros")
            return parametros

        except Exception as e:
            print(f"Error al cargar parámetros de fallecimiento: {e}")
            return {}

    def get_parametro(self, nombre_parametro: str, valor_default: Any = None) -> Any:
        """
        Obtiene un parámetro específico de fallecimiento

        Args:
            nombre_parametro: Nombre del parámetro a obtener
            valor_default: Valor por defecto si no se encuentra

        Returns:
            Valor del parámetro o valor por defecto
        """
        return self.parametros.get(nombre_parametro, valor_default)

    def get_parametros_disponibles(self) -> list:
        """
        Obtiene la lista de parámetros disponibles para fallecimiento

        Returns:
            Lista con los nombres de los parámetros
        """
        return list(self.parametros.keys())

    def validar_parametros_fallecimiento(self) -> bool:
        """
        Valida que los parámetros de fallecimiento sean correctos

        Returns:
            True si los parámetros son válidos, False en caso contrario
        """
        parametros_requeridos = [
            "gasto_adquisicion",
            "comision",
            "margen_solvencia",
            "tasa_costo_capital_tir",
            "moce",
        ]

        for param in parametros_requeridos:
            if param not in self.parametros:
                print(
                    f"Error: Parámetro requerido '{param}' no encontrado en fallecimiento"
                )
                return False

        return True

    def calcular_parametros_calculados(
        self,
        parametros_entrada: Dict[str, Any],
        tasas_interes_data: Dict[str, Any],
        producto,
    ) -> Dict[str, Any]:
        """
        Calcula todos los parámetros calculados específicos para fallecimiento

        Args:
            parametros_entrada: Parámetros de entrada del usuario
            tasas_interes_data: Datos de tasas de interés
            producto: Tipo de producto

        Returns:
            Diccionario con parámetros calculados de fallecimiento
        """
        try:
            # Usar el servicio centralizado para calcular todos los parámetros básicos
            parametros_calculados = (
                self.parametros_calculados_service.get_parametros_calculados(
                    parametros_entrada,
                    self.parametros,
                    tasas_interes_data,
                    producto,
                    "fallecimiento",
                )
            )

            # Aquí se pueden agregar cálculos específicos de fallecimiento
            # parametros_calculados["parametro_especifico_fallecimiento"] = self._calcular_algo_especifico()

            print(f"Parámetros calculados para fallecimiento: {parametros_calculados}")
            return parametros_calculados

        except Exception as e:
            print(f"Error específico en cobertura FALLECIMIENTO: {e}")
            print(f"Tipo de error: {type(e).__name__}")
            raise Exception(f"Error en cobertura FALLECIMIENTO: {e}") from e

    def calculo_actuarial(
        self,
        parametros_entrada: Dict[str, Any],
        parametros_almacenados: Dict[str, Any],
        parametros_calculados: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Ejecuta todos los cálculos actuariales para la cobertura de fallecimiento

        Args:
            parametros_entrada: Parámetros de entrada del usuario
            parametros_almacenados: Parámetros almacenados de la cobertura
            parametros_calculados: Parámetros calculados

        Returns:
            Diccionario con todos los resultados de cálculos actuariales
        """
        try:
            calculo_actuarial_service = CalculoActuarialService(
                parametros_entrada=parametros_entrada,
                parametros_almacenados=parametros_almacenados,
                parametros_calculados=parametros_calculados,
                producto=Producto.ENDOSOS,
                sexo=parametros_entrada.get("sexo"),
                fumador=parametros_entrada.get("fumador"),
                cobertura="fallecimiento",
            )

            # Calcular expuestos al mes
            expuestos_mes = calculo_actuarial_service.execute()

            # Aquí se pueden agregar más cálculos actuariales en el futuro
            # reserva_matematica = self._calcular_reserva_matematica()
            # prima_pura = self._calcular_prima_pura()
            # etc...

            resultados_actuariales = {
                "expuestos_mes": expuestos_mes,
                # "reserva_matematica": reserva_matematica,
                # "prima_pura": prima_pura,
            }

            return resultados_actuariales

        except Exception as e:
            print(f"Error en cálculos actuariales para FALLECIMIENTO: {e}")
            print(f"Tipo de error: {type(e).__name__}")
            raise Exception(f"Error en cálculos actuariales FALLECIMIENTO: {e}") from e
