"""
Módulo de modelos para el producto ENDOSOS
"""

from .endosos import (
    EndososOrchestrator,
    endosos_orchestrator,
    cotizar_endosos,
    get_endosos_info
)
from .core.response_building_step import (
    build_endosos_response,
    build_default_endosos_response,
    build_endosos_response_from_request
)

__all__ = [
    # Orquestador principal
    "EndososOrchestrator",
    "endosos_orchestrator", 
    "cotizar_endosos",
    "get_endosos_info",
    # Funciones de compatibilidad
    "build_endosos_response",
    "build_default_endosos_response", 
    "build_endosos_response_from_request"
]
