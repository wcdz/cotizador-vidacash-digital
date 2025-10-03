from abc import ABC, abstractmethod
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path


class DevolucionRepository(ABC):
    """Interfaz abstracta para el repositorio de devolución"""
    
    @abstractmethod
    def get_devolucion_data(self, producto: str, cobertura: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtiene todos los datos de devolución como una lista de diccionarios para un producto específico y opcionalmente cobertura"""
        pass
    
    @abstractmethod
    def get_devolucion_by_anio_poliza(self, producto: str, anio_poliza: int, cobertura: Optional[str] = None) -> Dict[str, Any]:
        """Obtiene los datos de devolución para un año específico de póliza de un producto y opcionalmente cobertura"""
        pass
    
    @abstractmethod
    def get_devolucion_valor(self, producto: str, anio_poliza: int, plazo_pago_primas: int, cobertura: Optional[str] = None) -> float:
        """Obtiene el valor de devolución para un año de póliza y plazo de pago de primas específicos de un producto y opcionalmente cobertura"""
        pass
    
    @abstractmethod
    def get_devolucion_by_producto_and_cobertura(self, producto: str, cobertura: str) -> List[Dict[str, Any]]:
        """Obtiene todos los datos de devolución para un producto y cobertura específica"""
        pass


class JsonDevolucionRepository(DevolucionRepository):
    """Implementación del repositorio de devolución usando archivo JSON"""
    
    def __init__(self, base_path: str = None):
        """
        Inicializa el repositorio de devolución
        
        Args:
            base_path: Ruta base para los archivos JSON (optional)
        """
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Ruta por defecto: raíz del proyecto / assets
            self.base_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / "assets"
        
        # Cache para evitar múltiples lecturas de disco por producto
        self._cache: Dict[str, List[Dict[str, Any]]] = {}
    
    def _get_devolucion_path(self, producto: str, cobertura: Optional[str] = None) -> Path:
        """Construye la ruta del archivo de devolución para un producto específico y opcionalmente cobertura"""
        if cobertura:
            # Si base_path ya incluye la ruta completa hasta la cobertura, solo agregar el nombre del archivo
            if "coberturas" in str(self.base_path):
                return self.base_path / "devolucion.json"
            else:
                # Ruta para coberturas: assets/productos/endosos/coberturas/fallecimiento/devolucion.json
                return (
                    self.base_path
                    / "productos"
                    / producto.lower()
                    / "coberturas"
                    / cobertura.lower()
                    / "devolucion.json"
                )
        else:
            # Ruta normal: assets/rumbo/devolucion.json
            return self.base_path / producto.lower() / "devolucion.json"
    
    def _cargar_devolucion_data(self, producto: str, cobertura: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Carga los datos de devolución desde el archivo JSON para un producto específico y opcionalmente cobertura
        """
        cache_key = f"{producto.lower()}_{cobertura.lower()}" if cobertura else producto.lower()
        
        # Si ya está en caché, devolver directamente
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        devolucion_path = self._get_devolucion_path(producto, cobertura)
        
        if not devolucion_path.exists():
            if cobertura:
                print(f"Archivo de devolución no encontrado: {devolucion_path}")
            self._cache[cache_key] = []
            return []
        
        try:
            with open(devolucion_path, "r", encoding="utf-8") as f:
                devolucion_data = json.load(f)
                self._cache[cache_key] = devolucion_data
                return devolucion_data
        except (json.JSONDecodeError, IOError) as e:
            context = f"{producto}/{cobertura}" if cobertura else producto
            print(f"Error cargando devolución {context}: {e}")
            self._cache[cache_key] = []
            return []
    
    def get_devolucion_data(self, producto: str, cobertura: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene todos los datos de devolución para un producto específico y opcionalmente cobertura
        Simula un SELECT * FROM devolucion WHERE producto = ? [AND cobertura = ?]
        """
        return self._cargar_devolucion_data(producto, cobertura)
    
    def get_devolucion_by_anio_poliza(self, producto: str, anio_poliza: int, cobertura: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene los datos de devolución para un año específico de póliza de un producto
        
        Args:
            producto: Nombre del producto
            anio_poliza: Año de póliza para el cual se quieren obtener los datos de devolución
            
        Returns:
            Diccionario con los datos de devolución del año de póliza solicitado
            
        Raises:
            ValueError: Si no se encuentra el año de póliza especificado
        """
        devolucion_data = self.get_devolucion_data(producto, cobertura)
        
        for item in devolucion_data:
            if item["año_poliza"] == anio_poliza:
                return item
        
        context = f"{producto}/{cobertura}" if cobertura else producto
        raise ValueError(f"No se encontraron datos de devolución para {context} y año de póliza {anio_poliza}")
    
    def get_devolucion_valor(self, producto: str, anio_poliza: int, plazo_pago_primas: int, cobertura: Optional[str] = None) -> float:
        """
        Obtiene el valor de devolución para un año de póliza y plazo de pago de primas específicos de un producto
        
        Args:
            producto: Nombre del producto
            anio_poliza: Año de póliza para el cual se quiere obtener el valor
            plazo_pago_primas: Plazo de pago de primas para el cual se quiere obtener el valor
            
        Returns:
            Valor de devolución como porcentaje (flotante)
            
        Raises:
            ValueError: Si no se encuentra el año de póliza o plazo de pago de primas especificado
        """
        try:
            item = self.get_devolucion_by_anio_poliza(producto, anio_poliza, cobertura)
            plazos = item.get("plazo_pago_primas", {})
            plazo_str = str(plazo_pago_primas)
            
            if plazo_str in plazos:
                return float(plazos[plazo_str])
            
            context = f"{producto}/{cobertura}" if cobertura else producto
            raise ValueError(f"No se encontró el plazo de pago de primas {plazo_pago_primas} para {context} y año de póliza {anio_poliza}")
            
        except ValueError as e:
            raise e
        except Exception as e:
            raise ValueError(f"Error al obtener valor de devolución: {str(e)}")
    
    def get_devolucion_by_producto_and_cobertura(self, producto: str, cobertura: str) -> List[Dict[str, Any]]:
        """
        Obtiene todos los datos de devolución para un producto y cobertura específica
        
        Args:
            producto: Nombre del producto (ej: "endosos")
            cobertura: Nombre de la cobertura (ej: "itp")
            
        Returns:
            Lista de diccionarios con datos de devolución
        """
        return self._cargar_devolucion_data(producto, cobertura)
    
    def limpiar_cache(self, producto: str = None, cobertura: Optional[str] = None):
        """Limpia la caché de devolución (útil para pruebas)"""
        if producto:
            if cobertura:
                cache_key = f"{producto.lower()}_{cobertura.lower()}"
                self._cache.pop(cache_key, None)
            else:
                # Limpiar todas las entradas que empiecen con el producto
                keys_to_remove = [k for k in self._cache.keys() if k.startswith(producto.lower())]
                for key in keys_to_remove:
                    self._cache.pop(key, None)
        else:
            self._cache.clear()


# Instancia global del repositorio
devolucion_repository = JsonDevolucionRepository() 