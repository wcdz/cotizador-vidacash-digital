"""
Módulo específico para la cobertura de ITP (Incapacidad Total y Permanente)
"""

from typing import Dict, Any
from src.infrastructure.repositories import get_repos


class ItpCobertura:
    """Clase específica para manejar la cobertura de ITP"""
    
    def __init__(self):
        self.producto = "endosos"
        self.cobertura = "itp"
        self.parametros = {}
    
    def cargar_parametros(self) -> Dict[str, Any]:
        """
        Carga los parámetros específicos para la cobertura de ITP
        
        Returns:
            Diccionario con los parámetros de ITP
        """
        try:
            # Obtener repositorios específicos para ITP
            repos = get_repos(self.producto, self.cobertura)
            
            # Obtener el repositorio de parámetros
            parametros_repo = repos.get("parametros")
            
            if parametros_repo is None:
                print(f"Error: No se encontró el repositorio de parámetros para {self.producto}/{self.cobertura}")
                return {}
            
            # Cargar parámetros específicos de ITP
            parametros = parametros_repo.get_parametros_by_producto_and_cobertura(
                self.producto, 
                self.cobertura
            )
            
            self.parametros = parametros
            print(f"Parámetros de ITP cargados: {len(parametros)} parámetros")
            return parametros
            
        except Exception as e:
            print(f"Error al cargar parámetros de ITP: {e}")
            return {}
    
    
    def get_parametro(self, nombre_parametro: str, valor_default: Any = None) -> Any:
        """
        Obtiene un parámetro específico de ITP
        
        Args:
            nombre_parametro: Nombre del parámetro a obtener
            valor_default: Valor por defecto si no se encuentra
            
        Returns:
            Valor del parámetro o valor por defecto
        """
        return self.parametros.get(nombre_parametro, valor_default)
    
    def get_parametros_disponibles(self) -> list:
        """
        Obtiene la lista de parámetros disponibles para ITP
        
        Returns:
            Lista con los nombres de los parámetros
        """
        return list(self.parametros.keys())
    
    def validar_parametros_itp(self) -> bool:
        """
        Valida que los parámetros de ITP sean correctos
        
        Returns:
            True si los parámetros son válidos, False en caso contrario
        """
        parametros_requeridos = [
            "tasa_costo_capital_tir", "comision", "margen_solvencia", 
            "tiene_asistencia", "costo_asistencia_funeraria"
        ]
        
        for param in parametros_requeridos:
            if param not in self.parametros:
                print(f"Error: Parámetro requerido '{param}' no encontrado en ITP")
                return False
        
        return True
    
    def calcular_prima_itp(self, suma_asegurada: float, edad: int, sexo: str) -> float:
        """
        Calcula la prima específica para ITP
        
        Args:
            suma_asegurada: Suma asegurada
            edad: Edad del asegurado
            sexo: Sexo del asegurado ('M' o 'F')
            
        Returns:
            Prima calculada para ITP
        """
        try:
            # Obtener parámetros base
            prima_base = self.get_parametro('prima_asignada', 0)
            comision = self.get_parametro('comision', 0)
            
            # Obtener factores específicos de ITP
            calculos = self.get_parametro('calculos_especificos', {})
            factor_edad = calculos.get('factor_edad', 1.0)
            factor_sexo = calculos.get('factor_sexo', 1.0)
            factor_ocupacion = calculos.get('factor_ocupacion', 1.0)
            
            # Aplicar factores específicos de ITP
            prima_ajustada = prima_base * factor_edad * factor_sexo * factor_ocupacion
            
            # Aplicar comisión
            prima_final = prima_ajustada * (1 + comision)
            
            return prima_final
            
        except Exception as e:
            print(f"Error al calcular prima de ITP: {e}")
            return 0.0
