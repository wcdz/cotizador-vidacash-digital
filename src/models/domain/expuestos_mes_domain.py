from typing import Dict, Any
import math


class ExpuestosMesDomain:
    """Dominio para cálculos actuariales de expuestos al mes en seguros de vida"""
    
    def calcular_mortalidad_anual(self, edad: int, sexo: str, fumador: bool, tabla_mortalidad: Dict[str, Any]) -> float:
        """
        Calcula la mortalidad anual para una edad específica
        
        Args:
            edad: Edad del asegurado
            sexo: Sexo del asegurado ("M" o "F")
            fumador: Si el asegurado es fumador (True) o no (False)
            tabla_mortalidad: Diccionario con los datos de mortalidad
            
        Returns:
            Tasa de mortalidad anual
        """
        try:
            edad_str = str(edad)
            if edad_str not in tabla_mortalidad:
                return 0.0
                
            # Determinar la clave correcta basada en sexo y estado de fumador
            if sexo == "M":
                clave_base = "hombres"
            else:
                clave_base = "mujeres"
                
            fumador_str = "fuma" if fumador else "no_fuma"
            clave = f"{clave_base}_{fumador_str}"
            
            if clave not in tabla_mortalidad[edad_str]:
                return 0.0
                
            return tabla_mortalidad[edad_str][clave]
        except (KeyError, ValueError, TypeError):
            return 0.0
    
    def calcular_mortalidad_mensual(self, mortalidad_anual: float) -> float:
        """
        Convierte mortalidad anual a mortalidad mensual
        
        Args:
            mortalidad_anual: Tasa de mortalidad anual
            
        Returns:
            Tasa de mortalidad mensual
        """
        if mortalidad_anual <= 0:
            return 0.0
        return (1 - (1 - mortalidad_anual / 1000) ** (1 / 12)) * 1000
    
    def calcular_mortalidad_ajustada(self, mortalidad_mensual: float, ajuste_mortalidad: float) -> float:
        """
        Aplica el ajuste de mortalidad a la mortalidad mensual
        
        Args:
            mortalidad_mensual: Tasa de mortalidad mensual
            ajuste_mortalidad: Factor de ajuste de mortalidad (ej: 1.2 para 20% más)
            
        Returns:
            Tasa de mortalidad mensual ajustada
        """
        return mortalidad_mensual * ajuste_mortalidad
    
    def calcular_fallecidos(self, vivos_inicio: float, mortalidad_ajustada: float) -> float:
        """
        Calcula el número de fallecidos en el mes
        
        Args:
            vivos_inicio: Número de vivos al inicio del mes
            mortalidad_ajustada: Tasa de mortalidad ajustada
            
        Returns:
            Número de fallecidos
        """
        return vivos_inicio * mortalidad_ajustada / 1000
    
    def calcular_vivos_despues_fallecidos(self, vivos_inicio: float, fallecidos: float) -> float:
        """
        Calcula los vivos después de restar los fallecidos
        
        Args:
            vivos_inicio: Número de vivos al inicio del mes
            fallecidos: Número de fallecidos en el mes
            
        Returns:
            Número de vivos después de fallecidos
        """
        return vivos_inicio - fallecidos
    
    def calcular_caducados(self, vivos_despues_fallecidos: float, caducidad_mensual: float) -> float:
        """
        Calcula el número de caducados en el mes
        
        Args:
            vivos_despues_fallecidos: Número de vivos después de fallecidos
            caducidad_mensual: Tasa de caducidad mensual
            
        Returns:
            Número de caducados
        """
        return caducidad_mensual * vivos_despues_fallecidos
    
    def calcular_vivos_finales(self, vivos_despues_fallecidos: float, caducados: float) -> float:
        """
        Calcula los vivos finales después de restar los caducados
        
        Args:
            vivos_despues_fallecidos: Número de vivos después de fallecidos
            caducados: Número de caducados en el mes
            
        Returns:
            Número de vivos finales
        """
        return vivos_despues_fallecidos - caducados
    
    def calcular_edad_actuarial(self, edad_inicial: int, mes: int) -> int:
        """
        Calcula la edad actuarial para un mes específico
        
        Args:
            edad_inicial: Edad inicial del asegurado
            mes: Mes de la proyección (1, 2, 3, ...)
            
        Returns:
            Edad actuarial para el mes
        """
        anio_poliza = math.ceil(mes / 12)
        return edad_inicial + anio_poliza - 1
    
    def calcular_tasa_caducidad_mensual(self, periodo_vigencia: int, caducidad_parametrizado_mensual: Dict[str, Any], caducidad_por_año: Dict[str, Any]) -> Dict[int, float]:
        """
        Calcula las tasas de caducidad mensual para todo el período
        
        Args:
            periodo_vigencia: Período de vigencia en años
            caducidad_parametrizado_mensual: Parámetros de caducidad mensual
            caducidad_por_año: Parámetros de caducidad anual
            
        Returns:
            Diccionario con las tasas de caducidad por mes
        """
        from src.helpers.caducidad_mensual import caducidad_mensual
        return caducidad_mensual(periodo_vigencia, caducidad_parametrizado_mensual, caducidad_por_año)