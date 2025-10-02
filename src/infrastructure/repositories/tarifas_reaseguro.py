from abc import ABC, abstractmethod
import json
import os
from typing import Dict, Any, Optional, List
from pathlib import Path


class TarifasReaseguroRepository(ABC):
    """Interfaz abstracta para el repositorio de tarifas de reaseguro"""

    @abstractmethod
    def get_tarifas_reaseguro(self) -> Dict[str, Any]:
        """Obtiene todas las tarifas de reaseguro como un diccionario"""
        pass

    @abstractmethod
    def get_tarifas_by_producto_and_cobertura(
        self, producto: str, cobertura: str
    ) -> Dict[str, Any]:
        """Obtiene todas las tarifas para un producto y cobertura específica"""
        pass

    @abstractmethod
    def get_tarifa_by_edad(
        self, producto: str, cobertura: str, edad: int, tipo_cobertura: str
    ) -> Optional[float]:
        """Obtiene una tarifa específica por edad, producto, cobertura y tipo de cobertura"""
        pass


class JsonTarifasReaseguroRepository(TarifasReaseguroRepository):
    """Implementación del repositorio de tarifas de reaseguro usando archivos JSON"""

    def __init__(self, base_path: str = None):
        """
        Inicializa el repositorio de tarifas de reaseguro

        Args:
            base_path: Ruta base para los archivos JSON (optional)
        """
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Ruta por defecto: raíz del proyecto / assets
            self.base_path = (
                Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
                / "assets"
            )

        # Cache para evitar múltiples lecturas de disco
        self._cache: Dict[str, Dict[str, Any]] = {}

    def _get_tarifas_path(self, producto: str, cobertura: str) -> Path:
        """Obtiene la ruta al archivo de tarifas de reaseguro para un producto y cobertura específica"""
        # Ruta: assets/coberturas_adicionales_producto/endosos/itp/tarifas_reaseguro.json
        return (
            self.base_path
            / "coberturas_adicionales_producto"
            / producto.lower()
            / cobertura.lower()
            / "tarifas_reaseguro.json"
        )

    def _cargar_tarifas(self, producto: str, cobertura: str) -> Dict[str, Any]:
        """
        Carga las tarifas de reaseguro desde el archivo JSON
        """
        cache_key = f"{producto.lower()}_{cobertura.lower()}"

        # Si ya está en caché, devolver directamente
        if cache_key in self._cache:
            return self._cache[cache_key]

        tarifas_path = self._get_tarifas_path(producto, cobertura)

        if not tarifas_path.exists():
            print(f"Archivo de tarifas no encontrado: {tarifas_path}")
            self._cache[cache_key] = {}
            return {}

        try:
            with open(tarifas_path, "r", encoding="utf-8") as f:
                tarifas = json.load(f)
                self._cache[cache_key] = tarifas
                return tarifas
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error cargando tarifas {producto}/{cobertura}: {e}")
            self._cache[cache_key] = {}
            return {}

    def get_tarifas_reaseguro(self) -> Dict[str, Any]:
        """
        Obtiene todas las tarifas de reaseguro (método por compatibilidad)
        Por defecto obtiene las tarifas de endosos/itp
        """
        return self.get_tarifas_by_producto_and_cobertura("endosos", "itp")

    def get_tarifas_by_producto_and_cobertura(
        self, producto: str, cobertura: str
    ) -> Dict[str, Any]:
        """
        Obtiene todas las tarifas para un producto y cobertura específica

        Args:
            producto: Nombre del producto (ej: "endosos")
            cobertura: Nombre de la cobertura (ej: "itp")

        Returns:
            Diccionario con todas las tarifas organizadas por edad
        """
        return self._cargar_tarifas(producto, cobertura)

    def get_tarifa_by_edad(
        self, producto: str, cobertura: str, edad: int, tipo_cobertura: str
    ) -> Optional[float]:
        """
        Obtiene una tarifa específica por edad, producto, cobertura y tipo de cobertura

        Args:
            producto: Nombre del producto (ej: "endosos")
            cobertura: Nombre de la cobertura (ej: "itp")
            edad: Edad del asegurado (ej: 25)
            tipo_cobertura: Tipo específico de cobertura (ej: "itp_anticipo_scor", "enf_graves_h_scor")

        Returns:
            Valor de la tarifa o None si no se encuentra
        """
        tarifas = self._cargar_tarifas(producto, cobertura)

        edad_str = str(edad)
        if edad_str not in tarifas:
            print(f"No se encontraron tarifas para la edad {edad}")
            return None

        tarifas_edad = tarifas[edad_str]
        if tipo_cobertura not in tarifas_edad:
            print(
                f"No se encontró el tipo de cobertura '{tipo_cobertura}' para la edad {edad}"
            )
            return None

        return tarifas_edad[tipo_cobertura]

    def get_tipos_cobertura_disponibles(
        self, producto: str, cobertura: str
    ) -> List[str]:
        """
        Obtiene todos los tipos de cobertura disponibles para un producto y cobertura

        Args:
            producto: Nombre del producto
            cobertura: Nombre de la cobertura

        Returns:
            Lista de tipos de cobertura disponibles
        """
        tarifas = self._cargar_tarifas(producto, cobertura)

        if not tarifas:
            return []

        # Obtener los tipos de cobertura de la primera edad disponible
        primera_edad = list(tarifas.keys())[0]
        return list(tarifas[primera_edad].keys())

    def get_edades_disponibles(self, producto: str, cobertura: str) -> List[int]:
        """
        Obtiene todas las edades disponibles para un producto y cobertura

        Args:
            producto: Nombre del producto
            cobertura: Nombre de la cobertura

        Returns:
            Lista de edades disponibles (ordenadas)
        """
        tarifas = self._cargar_tarifas(producto, cobertura)

        if not tarifas:
            return []

        edades = [int(edad) for edad in tarifas.keys() if edad.isdigit()]
        return sorted(edades)

    def limpiar_cache(self):
        """Limpia la caché de tarifas de reaseguro"""
        self._cache = {}


# Instancia global del repositorio
tarifas_reaseguro_repository = JsonTarifasReaseguroRepository()
