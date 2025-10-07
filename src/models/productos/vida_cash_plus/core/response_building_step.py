"""
Módulo para construir la respuesta de cotización de vida cash plus
"""

from typing import Dict, Any, List, Optional
from src.common.frecuencia_pago import FrecuenciaPago
from src.models.productos.vida_cash_plus.core.parameter_loading_step import ParameterLoadingStep


def _get_default_vida_cash_plus_values() -> Dict[str, Any]:
    """
    Obtiene los valores por defecto para el producto VIDA_CASH_PLUS

    Returns:
        Diccionario con valores por defecto
    """
    return {
        "moneda": "SOLES",
        "frecuencia_pago_primas": "MENSUAL",
        "fumador": False,
        "asistencia": False,
        "coberturas": ["fallecimiento", "itp"],
    }


def _load_parametros_almacenados_por_cobertura(coberturas: List[str]) -> Dict[str, Any]:
    """
    Carga los parámetros almacenados para cada cobertura especificada
    
    Args:
        coberturas: Lista de coberturas para cargar parámetros
        
    Returns:
        Diccionario con parámetros organizados por cobertura en orden específico
    """
    # Definir el orden específico de las coberturas
    orden_coberturas = ["fallecimiento", "itp"]
    
    # Ordenar las coberturas según el orden especificado
    coberturas_ordenadas = []
    for cobertura in orden_coberturas:
        if cobertura in coberturas:
            coberturas_ordenadas.append(cobertura)
    
    # Agregar cualquier cobertura que no esté en el orden específico
    for cobertura in coberturas:
        if cobertura not in coberturas_ordenadas:
            coberturas_ordenadas.append(cobertura)
    
    parametros_almacenados = {
        "coberturas": {}
    }
    
    for cobertura in coberturas_ordenadas:
        try:
            # Crear instancia del ParameterLoadingStep para esta cobertura
            step = ParameterLoadingStep("vida_cash_plus", cobertura)
            
            # Cargar parámetros para esta cobertura
            parametros_cobertura = step.execute()
            
            if parametros_cobertura:
                parametros_almacenados["coberturas"][cobertura] = parametros_cobertura
                print(f"Parámetros cargados para cobertura '{cobertura}': {len(parametros_cobertura)} parámetros")
            else:
                print(f"Advertencia: No se pudieron cargar parámetros para la cobertura '{cobertura}'")
                parametros_almacenados["coberturas"][cobertura] = {}
                
        except Exception as e:
            print(f"Error al cargar parámetros para cobertura '{cobertura}': {e}")
            parametros_almacenados["coberturas"][cobertura] = {}
    
    return parametros_almacenados


def build_vida_cash_plus_response(
    parametros_entrada: Dict[str, Any],
    parametros_almacenados: Dict[str, Any],
    parametros_calculados: Dict[str, Any],
    vida_cash_plus: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Construye la respuesta completa de cotización para el producto VIDA_CASH_PLUS

    Args:
        parametros_entrada: Parámetros de entrada del usuario
        parametros_almacenados: Parámetros almacenados en la base de datos
        parametros_calculados: Parámetros calculados durante la cotización
        vida_cash_plus: Datos específicos de vida cash plus calculados

    Returns:
        Diccionario con la respuesta completa de cotización
    """

    # Estructura base de la respuesta
    response = {
        "producto": "VIDA_CASH_PLUS",
        "parametros_entrada": parametros_entrada,
        "parametros_almacenados": parametros_almacenados,
        "parametros_calculados": parametros_calculados,
        "vida_cash_plus": vida_cash_plus,
    }

    return response


def build_default_vida_cash_plus_response() -> Dict[str, Any]:
    """
    Construye una respuesta de ejemplo para VIDA_CASH_PLUS con datos por defecto

    Returns:
        Diccionario con la respuesta de ejemplo
    """

    # Parámetros de entrada de ejemplo
    parametros_entrada = {
        **_get_default_vida_cash_plus_values(),
        "edad_actuarial": 28,
        "periodo_vigencia": 15,
        "periodo_pago_primas": 15,
        "suma_asegurada": 200000.0,
        "sexo": "M",
        "porcentaje_devolucion": 125.0,
    }

    # Cargar parámetros almacenados dinámicamente
    coberturas = parametros_entrada.get("coberturas", ["fallecimiento", "itp"])
    parametros_almacenados = _load_parametros_almacenados_por_cobertura(coberturas)

    # Parámetros calculados de ejemplo
    parametros_calculados = {
        "coberturas": {
            "fallecimiento": {
                "adquisicion_fijo_poliza": 69.4175545055428,
                "mantenimiento_poliza": 0.0,
                "tasa_costo_capital_mensual": 0.005453246537902023,
                "inflacion_mensual": 0.0,
                "reserva": 0.2575,
                "tasa_interes_anual": 5.0,
                "tasa_interes_mensual": 0.004564132725388248,
                "tasa_inversion": 0.055,
                "tasa_costo_capital_mes": 0.01171491691985338,
                "factor_pago": 0.1,
                "prima_para_redondeo": 13.1865780424015,
            },
            "itp": {
                "adquisicion_fijo_poliza": 0.0,
                "mantenimiento_poliza": 0.0,
                "tasa_costo_capital_mensual": 0.004867550565343048,
                "inflacion_mensual": 0.0,
                "reserva": 0.0675,
                "tasa_interes_anual": 5.0,
                "tasa_interes_mensual": 0.0040741237836483535,
                "tasa_inversion": 0.055,
                "tasa_costo_capital_mes": 0.010087720864679683,
                "factor_pago": 0.1,
                "prima_para_redondeo": 13.1865780424015,
            },
        }
    }

    # Datos de vida cash plus calculados de ejemplo
    vida_cash_plus = {
        "coberturas": {
            "fallecimiento": {
                "tasas": {
                    "mensual": 6.59328902120075e-05,
                    "trimestral": 0.000184612092593621,
                    "semestral": 0.00035603760714484045,
                    "anual": 0.000659328902120075,
                },
                "devoluciones": {
                    "mensual": 2966.980059540337,
                    "trimestral": 2769.181388904315,
                    "semestral": 2670.2820535863034,
                    "anual": 2472.483382950281,
                },
                "primas_anualizadas": {
                    "mensual": 131.86578042401499,
                    "trimestral": 131.86578042401499,
                    "semestral": 131.86578042401499,
                    "anual": 131.86578042401499,
                },
                "primas_frecuencializadas": {
                    "mensual": 13.1865780424015,
                    "trimestral": 36.9224185187242,
                    "semestral": 71.20752142896809,
                    "anual": 131.86578042401499,
                },
            },
            "itp": {"primas_frecuencializadas": {}},
        },
        "tabla_devolucion": "",
    }

    return build_vida_cash_plus_response(
        parametros_entrada, parametros_almacenados, parametros_calculados, vida_cash_plus
    )


def build_vida_cash_plus_response_from_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Construye la respuesta de VIDA_CASH_PLUS basada en los datos de la petición

    Args:
        request_data: Datos de la petición HTTP

    Returns:
        Diccionario con la respuesta de cotización
    """

    # Construir parámetros de entrada combinando request_data con defaults
    parametros_entrada = {
        **_get_default_vida_cash_plus_values(),
        **{k: v for k, v in request_data.items() if v is not None},
    }

    # Obtener las coberturas de los parámetros de entrada
    coberturas = parametros_entrada.get("coberturas", ["fallecimiento", "itp"])
    
    # Cargar parámetros almacenados dinámicamente para cada cobertura
    parametros_almacenados = _load_parametros_almacenados_por_cobertura(coberturas)
    
    # Inicializar estructuras vacías para parámetros calculados y vida cash plus
    parametros_calculados = {
        "coberturas": {cobertura: {} for cobertura in coberturas}
    }
    
    vida_cash_plus = {
        "coberturas": {cobertura: {} for cobertura in coberturas},
        "tabla_devolucion": ""
    }

    return build_vida_cash_plus_response(
        parametros_entrada, parametros_almacenados, parametros_calculados, vida_cash_plus
    )
