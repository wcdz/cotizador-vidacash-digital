"""
Módulo específico para la cobertura de fallecimiento
"""

from typing import Dict, Any
from src.infrastructure.repositories import get_repos


class FallecimientoCobertura:
    """Clase específica para manejar la cobertura de fallecimiento"""
    
    def __init__(self):
        self.producto = "endosos"
        self.cobertura = "fallecimiento"
        self.parametros = {}
    
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
                print(f"Error: No se encontró el repositorio de parámetros para {self.producto}/{self.cobertura}")
                return {}
            
            # Cargar parámetros específicos de fallecimiento
            parametros = parametros_repo.get_parametros_by_producto_and_cobertura(
                self.producto, 
                self.cobertura
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
            "gasto_adquisicion", "comision", "margen_solvencia", 
            "tasa_costo_capital_tir", "moce"
        ]
        
        for param in parametros_requeridos:
            if param not in self.parametros:
                print(f"Error: Parámetro requerido '{param}' no encontrado en fallecimiento")
                return False
        
        return True
