"""
Orquestador principal para el producto ENDOSOS
"""

from typing import Dict, Any, List
from src.models.productos.endosos.core.parameter_loading_step import (
    ParameterLoadingStep,
)
from src.models.productos.endosos.core.response_building_step import (
    build_endosos_response,
    _get_default_endosos_values,
    _load_parametros_almacenados_por_cobertura,
)
from src.infrastructure.repositories.repos import get_repos


class EndososOrchestrator:
    """
    Orquestador principal para el producto ENDOSOS.
    Coordina la carga de parámetros y construcción de respuestas.
    """

    def __init__(self):
        self.producto = "endosos"
        self._coberturas_disponibles = None

    def _cargar_coberturas_disponibles(self) -> List[str]:
        """
        Carga las coberturas disponibles desde el repositorio

        Returns:
            Lista de coberturas disponibles para el producto
        """
        if self._coberturas_disponibles is None:
            try:
                repos = get_repos(self.producto)
                coberturas_repo = repos["coberturas"]
                self._coberturas_disponibles = (
                    coberturas_repo.get_coberturas_by_producto(self.producto)
                )
                print(
                    f"Coberturas cargadas para {self.producto}: {self._coberturas_disponibles}"
                )
            except Exception as e:
                print(f"Error al cargar coberturas: {e}")
                # Fallback a coberturas por defecto
                self._coberturas_disponibles = ["fallecimiento", "itp"]

        return self._coberturas_disponibles

    def cotizar(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal para realizar cotizaciones de endosos

        Args:
            request_data: Datos de la petición de cotización

        Returns:
            Diccionario con la respuesta completa de cotización
        """
        try:
            # 1. Preparar parámetros de entrada
            parametros_entrada = self._preparar_parametros_entrada(request_data)

            # 2. Cargar parámetros almacenados por cobertura
            parametros_almacenados = self._cargar_parametros_almacenados(
                parametros_entrada
            )

            # 3. Calcular parámetros específicos
            parametros_calculados = self._calcular_parametros(
                parametros_entrada, parametros_almacenados
            )

            # 4. Calcular datos específicos de endosos
            endosos_data = self._calcular_endosos(
                parametros_entrada, parametros_almacenados, parametros_calculados
            )

            # 5. Construir respuesta final
            response = build_endosos_response(
                parametros_entrada=parametros_entrada,
                parametros_almacenados=parametros_almacenados,
                parametros_calculados=parametros_calculados,
                endosos=endosos_data,
            )

            return response

        except Exception as e:
            print(f"Error en orquestación de endosos: {e}")
            raise

    def _preparar_parametros_entrada(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepara los parámetros de entrada combinando request_data con valores por defecto

        Args:
            request_data: Datos de la petición

        Returns:
            Parámetros de entrada preparados en el orden especificado
        """
        # Obtener valores por defecto
        valores_default = _get_default_endosos_values()

        # Definir el orden específico de los parámetros
        orden_parametros = [
            "edad_actuarial",
            "moneda",
            "periodo_vigencia",
            "periodo_pago_primas",
            "suma_asegurada",
            "sexo",
            "frecuencia_pago_primas",
            "fumador",
            "asistencia",
            "porcentaje_devolucion",
            "coberturas",
        ]

        # Crear diccionario ordenado
        parametros_entrada = {}

        for param in orden_parametros:
            if param in request_data and request_data[param] is not None:
                # Usar valor de la petición si existe y no es None
                parametros_entrada[param] = request_data[param]
            elif param in valores_default:
                # Usar valor por defecto
                parametros_entrada[param] = valores_default[param]

        # Procesar coberturas específicamente
        if "coberturas" in parametros_entrada:
            coberturas = parametros_entrada["coberturas"]
            if isinstance(coberturas, list):
                # Cargar coberturas disponibles dinámicamente
                coberturas_disponibles = self._cargar_coberturas_disponibles()
                
                # Convertir array a objeto con claves ordenadas según coberturas disponibles
                coberturas_obj = {}
                for cobertura in coberturas_disponibles:
                    coberturas_obj[cobertura] = cobertura in coberturas
                
                parametros_entrada["coberturas"] = coberturas_obj

        return parametros_entrada

    def _cargar_parametros_almacenados(
        self, parametros_entrada: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Carga los parámetros almacenados para las coberturas especificadas

        Args:
            parametros_entrada: Parámetros de entrada

        Returns:
            Parámetros almacenados organizados por cobertura
        """
        # Obtener coberturas del nuevo formato
        coberturas_obj = parametros_entrada.get("coberturas", {})

        if isinstance(coberturas_obj, dict):
            # Nuevo formato: {"itp": true, "fallecimiento": true}
            coberturas = [k for k, v in coberturas_obj.items() if v]
        else:
            # Formato legacy: ["itp", "fallecimiento"]
            coberturas = (
                coberturas_obj
                if isinstance(coberturas_obj, list)
                else self._cargar_coberturas_disponibles()
            )

        return _load_parametros_almacenados_por_cobertura(coberturas)

    def _calcular_parametros(
        self, parametros_entrada: Dict[str, Any], parametros_almacenados: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcula parámetros específicos basados en los parámetros de entrada y almacenados

        Args:
            parametros_entrada: Parámetros de entrada
            parametros_almacenados: Parámetros almacenados

        Returns:
            Parámetros calculados
        """
        # Obtener coberturas del nuevo formato
        coberturas_obj = parametros_entrada.get("coberturas", {})

        if isinstance(coberturas_obj, dict):
            # Nuevo formato: {"itp": true, "fallecimiento": true}
            coberturas = [k for k, v in coberturas_obj.items() if v]
        else:
            # Formato legacy: ["itp", "fallecimiento"]
            coberturas = (
                coberturas_obj
                if isinstance(coberturas_obj, list)
                else self._cargar_coberturas_disponibles()
            )

        parametros_calculados = {"coberturas": {}}

        # Ordenar coberturas según el orden específico
        orden_coberturas = ["fallecimiento", "itp"]
        coberturas_ordenadas = []
        for cobertura in orden_coberturas:
            if cobertura in coberturas:
                coberturas_ordenadas.append(cobertura)
        for cobertura in coberturas:
            if cobertura not in coberturas_ordenadas:
                coberturas_ordenadas.append(cobertura)

        for cobertura in coberturas_ordenadas:
            # Aquí se implementarían los cálculos específicos por cobertura
            # Por ahora, inicializamos con estructura vacía
            parametros_calculados["coberturas"][cobertura] = {
                "calculado_por": "EndososOrchestrator",
                "timestamp": "2024-01-01T00:00:00Z",  # Placeholder
            }

        return parametros_calculados

    def _calcular_endosos(
        self,
        parametros_entrada: Dict[str, Any],
        parametros_almacenados: Dict[str, Any],
        parametros_calculados: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calcula los datos específicos de endosos

        Args:
            parametros_entrada: Parámetros de entrada
            parametros_almacenados: Parámetros almacenados
            parametros_calculados: Parámetros calculados

        Returns:
            Datos específicos de endosos
        """
        # Obtener coberturas del nuevo formato
        coberturas_obj = parametros_entrada.get("coberturas", {})

        if isinstance(coberturas_obj, dict):
            # Nuevo formato: {"itp": true, "fallecimiento": true}
            coberturas = [k for k, v in coberturas_obj.items() if v]
        else:
            # Formato legacy: ["itp", "fallecimiento"]
            coberturas = (
                coberturas_obj
                if isinstance(coberturas_obj, list)
                else self._cargar_coberturas_disponibles()
            )

        endosos_data = {
            "coberturas": {},
            "tabla_devolucion": "",
            "calculado_por": "EndososOrchestrator",
        }

        # Ordenar coberturas según el orden específico
        orden_coberturas = ["fallecimiento", "itp"]
        coberturas_ordenadas = []
        for cobertura in orden_coberturas:
            if cobertura in coberturas:
                coberturas_ordenadas.append(cobertura)
        for cobertura in coberturas:
            if cobertura not in coberturas_ordenadas:
                coberturas_ordenadas.append(cobertura)

        for cobertura in coberturas_ordenadas:
            # Aquí se implementarían los cálculos específicos de endosos por cobertura
            # Por ahora, inicializamos con estructura vacía
            endosos_data["coberturas"][cobertura] = {
                "calculado_por": "EndososOrchestrator",
                "cobertura": cobertura,
            }

        return endosos_data

    def get_cobertura_info(self, cobertura: str) -> Dict[str, Any]:
        """
        Obtiene información específica de una cobertura

        Args:
            cobertura: Nombre de la cobertura

        Returns:
            Información de la cobertura
        """
        if cobertura not in self._cargar_coberturas_disponibles():
            raise ValueError(f"Cobertura '{cobertura}' no soportada")

        # Cargar parámetros de la cobertura específica
        step = ParameterLoadingStep(self.producto, cobertura)
        parametros = step.execute()

        return {
            "cobertura": cobertura,
            "parametros": parametros,
            "parametros_disponibles": step.get_parametros_disponibles(),
            "es_fallecimiento": step.es_fallecimiento(),
            "es_itp": step.es_itp(),
        }

    def get_coberturas_disponibles(self) -> List[str]:
        """
        Obtiene la lista de coberturas disponibles

        Returns:
            Lista de coberturas disponibles
        """
        return self._cargar_coberturas_disponibles().copy()


# Instancia global del orquestador
endosos_orchestrator = EndososOrchestrator()


# Funciones de conveniencia para mantener compatibilidad
def cotizar_endosos(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Función de conveniencia para cotizar endosos

    Args:
        request_data: Datos de la petición

    Returns:
        Respuesta de cotización
    """
    return endosos_orchestrator.cotizar(request_data)


def get_endosos_info() -> Dict[str, Any]:
    """
    Obtiene información general del producto endosos

    Returns:
        Información del producto
    """
    return {
        "producto": "endosos",
        "coberturas_disponibles": endosos_orchestrator.get_coberturas_disponibles(),
        "descripcion": "Producto de seguros de endosos",
        "version": "1.0.0",
    }
