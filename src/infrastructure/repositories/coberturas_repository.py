from abc import ABC, abstractmethod
import json
import os
from typing import Dict, Any, List, Optional
from pathlib import Path


class CoberturasRepository(ABC):
    """Interfaz abstracta para el repositorio de coberturas"""
    
    @abstractmethod
    def get_coberturas_by_producto(self, producto: str) -> List[str]:
        """Obtiene todas las coberturas disponibles para un producto específico"""
        pass
    
    @abstractmethod
    def get_coberturas_info(self, producto: str) -> Dict[str, Any]:
        """Obtiene información completa de coberturas para un producto"""
        pass
    
    @abstractmethod
    def cobertura_existe(self, producto: str, cobertura: str) -> bool:
        """Verifica si una cobertura existe para un producto específico"""
        pass


class JsonCoberturasRepository(CoberturasRepository):
    """Implementación del repositorio de coberturas usando archivos JSON"""
    
    def __init__(self, base_path: str = None):
        """
        Inicializa el repositorio de coberturas
        
        Args:
            base_path: Ruta base para los archivos JSON (optional)
        """
        if base_path:
            self.base_path = Path(base_path)
        else:
            # Ruta por defecto: raíz del proyecto / assets
            self.base_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))) / "assets"
        
        # Cache para evitar múltiples lecturas de disco
        self._cache: Dict[str, List[str]] = {}
    
    def _get_coberturas_path(self, producto: str) -> Path:
        """Obtiene la ruta al archivo de coberturas para un producto"""
        return self.base_path / "productos" / producto.lower() / "coberturas.json"
    
    def _cargar_coberturas(self, producto: str) -> List[str]:
        """
        Carga las coberturas desde el archivo JSON
        """
        producto = producto.lower()
        
        # Si ya está en caché, devolver directamente
        if producto in self._cache:
            return self._cache[producto]
        
        coberturas_path = self._get_coberturas_path(producto)
        
        if not coberturas_path.exists():
            print(f"Archivo de coberturas no encontrado: {coberturas_path}")
            self._cache[producto] = []
            return []
        
        try:
            with open(coberturas_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                coberturas = data.get("coberturas", [])
                self._cache[producto] = coberturas
                return coberturas
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error al cargar coberturas para {producto}: {e}")
            self._cache[producto] = []
            return []
    
    def get_coberturas_by_producto(self, producto: str) -> List[str]:
        """
        Obtiene todas las coberturas disponibles para un producto específico
        
        Args:
            producto: Nombre del producto
            
        Returns:
            Lista de coberturas disponibles
        """
        return self._cargar_coberturas(producto)
    
    def get_coberturas_info(self, producto: str) -> Dict[str, Any]:
        """
        Obtiene información completa de coberturas para un producto
        
        Args:
            producto: Nombre del producto
            
        Returns:
            Diccionario con información de coberturas
        """
        coberturas = self._cargar_coberturas(producto)
        
        return {
            "producto": producto,
            "coberturas": coberturas,
            "total_coberturas": len(coberturas),
            "coberturas_disponibles": coberturas
        }
    
    def cobertura_existe(self, producto: str, cobertura: str) -> bool:
        """
        Verifica si una cobertura existe para un producto específico
        
        Args:
            producto: Nombre del producto
            cobertura: Nombre de la cobertura
            
        Returns:
            True si la cobertura existe, False en caso contrario
        """
        coberturas = self._cargar_coberturas(producto)
        return cobertura.lower() in [c.lower() for c in coberturas]
    
    def get_coberturas_ordenadas(self, producto: str, orden: List[str] = None) -> List[str]:
        """
        Obtiene las coberturas ordenadas según un orden específico
        
        Args:
            producto: Nombre del producto
            orden: Lista con el orden deseado (opcional)
            
        Returns:
            Lista de coberturas ordenadas
        """
        coberturas = self._cargar_coberturas(producto)
        
        if not orden:
            return coberturas
        
        # Ordenar según el orden especificado
        coberturas_ordenadas = []
        for cobertura in orden:
            if cobertura in coberturas:
                coberturas_ordenadas.append(cobertura)
        
        # Agregar coberturas que no estén en el orden especificado
        for cobertura in coberturas:
            if cobertura not in coberturas_ordenadas:
                coberturas_ordenadas.append(cobertura)
        
        return coberturas_ordenadas
    
    def limpiar_cache(self):
        """Limpia la caché de coberturas (útil para pruebas)"""
        self._cache = {}


# Instancia global del repositorio
coberturas_repository = JsonCoberturasRepository()
