"""
Enum para frecuencias de pago
"""
from enum import Enum


class FrecuenciaPago(str, Enum):
    """Enum para las frecuencias de pago de primas"""
    
    ANUAL = "ANUAL"
    SEMESTRAL = "SEMESTRAL"
    TRIMESTRAL = "TRIMESTRAL"
    MENSUAL = "MENSUAL"
    BIMESTRAL = "BIMESTRAL"
