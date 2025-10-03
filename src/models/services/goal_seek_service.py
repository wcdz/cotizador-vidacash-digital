from typing import Dict, Any
from src.models.domain.goal_seek_domain import GoalSeekDomain


class GoalSeekService:
    """
    Servicio que orquesta la ejecución del Goal Seek para encontrar el valor de prima_asignada
    que hace que el VNA se acerque más a cero.
    """
    
    def __init__(self):
        self.goal_seek_domain = GoalSeekDomain()
    
    def execute(
        self, 
        parametros_entrada: Dict[str, Any], 
        parametros_almacenados: Dict[str, Any], 
        parametros_calculados: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ejecuta el Goal Seek para encontrar la prima_asignada óptima.
        
        Args:
            parametros_entrada: Parámetros de entrada del usuario
            parametros_almacenados: Parámetros almacenados
            parametros_calculados: Parámetros calculados
            
        Returns:
            Diccionario con la prima_asignada óptima y el VNA resultante
        """
        return self.goal_seek_domain.execute_goal_seek(
            parametros_entrada,
            parametros_almacenados,
            parametros_calculados
        )
