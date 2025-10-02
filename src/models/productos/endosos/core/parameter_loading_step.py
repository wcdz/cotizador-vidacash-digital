from src.infrastructure.repositories import get_repos
from typing import Dict, Any, Optional
from src.models.productos.endosos.coberturas import FallecimientoCobertura, ItpCobertura


class ParameterLoadingStep:
    producto: str
    cobertura: str
    parametros: Dict[str, Any]

    def __init__(self, producto: str, cobertura: str):
        """
        Inicializa el paso de carga de parámetros

        Args:
            producto: Nombre del producto (ej: "endosos")
            cobertura: Nombre de la cobertura (ej: "fallecimiento", "itp")
        """
        self.producto = producto
        self.cobertura = cobertura
        self.parametros = {}

    def execute(self) -> Dict[str, Any]:
        """
        Ejecuta el paso de carga de parámetros

        Returns:
            Diccionario con los parámetros cargados
        """
        self.parametros = self.get_parametros_almacenados()
        return self.parametros

    def get_parametros_almacenados(self) -> Dict[str, Any]:
        """
        Obtiene los parámetros almacenados para el producto y cobertura específicos
        usando los módulos específicos por cobertura

        Returns:
            Diccionario con los parámetros cargados desde el archivo JSON y específicos de la cobertura
        """
        try:
            # Obtener la instancia específica de la cobertura
            cobertura_instance = self._get_cobertura_instance()

            if cobertura_instance is None:
                print(f"Error: Cobertura '{self.cobertura}' no soportada")
                return {}

            # Cargar parámetros usando el módulo específico de la cobertura
            parametros = cobertura_instance.cargar_parametros()

            # Validar parámetros específicos de la cobertura
            if hasattr(cobertura_instance, f"validar_parametros_{self.cobertura}"):
                valido = getattr(
                    cobertura_instance, f"validar_parametros_{self.cobertura}"
                )()
                if not valido:
                    print(f"Advertencia: Parámetros de {self.cobertura} no son válidos")

            return parametros

        except Exception as e:
            print(
                f"Error al cargar parámetros para {self.producto}/{self.cobertura}: {e}"
            )
            return {}

    def _get_cobertura_instance(self):
        """
        Obtiene la instancia específica de la cobertura

        Returns:
            Instancia de la clase específica de la cobertura o None si no es soportada
        """
        coberturas_soportadas = {
            "fallecimiento": FallecimientoCobertura,
            "itp": ItpCobertura,
        }

        cobertura_class = coberturas_soportadas.get(self.cobertura.lower())

        if cobertura_class is None:
            return None

        return cobertura_class()

    def get_parametro(self, nombre_parametro: str, valor_default: Any = None) -> Any:
        """
        Obtiene un parámetro específico de los ya cargados

        Args:
            nombre_parametro: Nombre del parámetro a obtener
            valor_default: Valor por defecto si no se encuentra el parámetro

        Returns:
            Valor del parámetro o valor por defecto
        """
        return self.parametros.get(nombre_parametro, valor_default)

    def get_parametros_disponibles(self) -> list:
        """
        Obtiene la lista de nombres de parámetros disponibles

        Returns:
            Lista con los nombres de los parámetros cargados
        """
        return list(self.parametros.keys())

    def get_cobertura_instance(self):
        """
        Obtiene la instancia específica de la cobertura para acceso a métodos específicos

        Returns:
            Instancia de la clase específica de la cobertura
        """
        return self._get_cobertura_instance()

    def es_fallecimiento(self) -> bool:
        """
        Verifica si la cobertura actual es fallecimiento

        Returns:
            True si es fallecimiento, False en caso contrario
        """
        return self.cobertura.lower() == "fallecimiento"

    def es_itp(self) -> bool:
        """
        Verifica si la cobertura actual es ITP

        Returns:
            True si es ITP, False en caso contrario
        """
        return self.cobertura.lower() == "itp"
