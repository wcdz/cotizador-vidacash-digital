"""
Acceso simple a repositorios por producto y cobertura
"""
import os
from pathlib import Path
from .caducidad_repository import JsonCaducidadRepository
from .devolucion_repository import JsonDevolucionRepository
from .parametros_repository import JsonParametrosRepository
from .tabla_mortalidad_repository import JsonTablaMortalidadRepository
from .tasa_interes_repository import JsonTasaInteresRepository
from .tarifas_reaseguro import JsonTarifasReaseguroRepository
from .factores_pago_repository import JsonFactoresPagoRepository
from .periodos_cotizacion_repository import JsonPeriodosCotizacionRepository
from .coberturas_repository import JsonCoberturasRepository


def get_repos(producto: str, cobertura: str = None):
    """
    Obtiene todos los repositorios para un producto y cobertura específicos
    
    Args:
        producto: Nombre del producto (ej: "endosos")
        cobertura: Nombre de la cobertura (ej: "fallecimiento", "itp") - opcional
    
    Returns:
        Diccionario con todos los repositorios
    """
    # Ruta base del proyecto
    base_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
    
    if cobertura:
        # Para coberturas específicas: assets/productos/endosos/coberturas/fallecimiento/
        ruta = base_path / "assets" / "productos" / producto.lower() / "coberturas" / cobertura.lower()
    else:
        # Para productos generales: assets/endosos/
        ruta = base_path / "assets" / producto.lower()
    
    return {
        "caducidad": JsonCaducidadRepository(str(ruta), producto, [cobertura] if cobertura else None),
        "devolucion": JsonDevolucionRepository(str(ruta)),
        "parametros": JsonParametrosRepository(str(ruta)),
        "tabla_mortalidad": JsonTablaMortalidadRepository(str(ruta), producto),
        "tasa_interes": JsonTasaInteresRepository(str(ruta), producto),
        "tarifas_reaseguro": JsonTarifasReaseguroRepository(str(ruta)) if cobertura else None,
        "factores_pago": JsonFactoresPagoRepository(str(base_path / "assets" / "cross"), "cross"),
        "periodos_cotizacion": JsonPeriodosCotizacionRepository(str(ruta), producto),
        "coberturas": JsonCoberturasRepository(str(base_path / "assets"))
    }


# Funciones de conveniencia para los casos más comunes
def get_fallecimiento_repos():
    """Obtiene repositorios para endosos/fallecimiento"""
    return get_repos("endosos", "fallecimiento")

def get_itp_repos():
    """Obtiene repositorios para endosos/itp"""
    return get_repos("endosos", "itp")

def get_endosos_repos():
    """Obtiene repositorios generales para endosos"""
    return get_repos("endosos")
