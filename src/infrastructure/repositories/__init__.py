"""
Módulo de repositorios para el sistema de cotización
"""

# Repositorios individuales
from .caducidad_repository import CaducidadRepository, JsonCaducidadRepository, caducidad_repository
from .devolucion_repository import DevolucionRepository, JsonDevolucionRepository, devolucion_repository
from .parametros_repository import ParametrosRepository, JsonParametrosRepository, parametros_repository
from .tabla_mortalidad_repository import TablaMortalidadRepository, JsonTablaMortalidadRepository, tabla_mortalidad_repository
from .tasa_interes_repository import TasaInteresRepository, JsonTasaInteresRepository, tasa_interes_repository
from .tarifas_reaseguro import TarifasReaseguroRepository, JsonTarifasReaseguroRepository, tarifas_reaseguro_repository
from .factores_pago_repository import FactoresPagoRepository, JsonFactoresPagoRepository, factores_pago_repository
from .periodos_cotizacion_repository import PeriodosCotizacionRepository, JsonPeriodosCotizacionRepository, periodos_cotizacion_repository

# Acceso simple por producto/cobertura
from .repos import get_repos, get_fallecimiento_repos, get_itp_repos, get_endosos_repos

__all__ = [
    # Repositorios individuales
    "CaducidadRepository",
    "JsonCaducidadRepository", 
    "caducidad_repository",
    "DevolucionRepository",
    "JsonDevolucionRepository",
    "devolucion_repository",
    "ParametrosRepository",
    "JsonParametrosRepository",
    "parametros_repository",
    "TablaMortalidadRepository",
    "JsonTablaMortalidadRepository",
    "tabla_mortalidad_repository",
    "TasaInteresRepository",
    "JsonTasaInteresRepository",
    "tasa_interes_repository",
    "TarifasReaseguroRepository",
    "JsonTarifasReaseguroRepository",
    "tarifas_reaseguro_repository",
    "FactoresPagoRepository",
    "JsonFactoresPagoRepository",
    "factores_pago_repository",
    "PeriodosCotizacionRepository",
    "JsonPeriodosCotizacionRepository",
    "periodos_cotizacion_repository",
    
    # Acceso simple
    "get_repos",
    "get_fallecimiento_repos",
    "get_itp_repos", 
    "get_endosos_repos"
]
