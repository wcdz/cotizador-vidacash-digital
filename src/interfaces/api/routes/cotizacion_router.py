"""
Router para cotizaciones de seguros
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.infrastructure.repositories import (
    get_fallecimiento_repos,
    get_itp_repos,
    get_repos,
)
from src.models.productos.endosos import cotizar_endosos, get_endosos_info
from src.models.productos.vida_cash_plus import (
    cotizar_vida_cash_plus,
    get_vida_cash_plus_info,
)
from src.common.producto import Producto

router = APIRouter(prefix="/api/v1/productos", tags=["cotizaciones"])


class ParametrosCotizacion(BaseModel):
    edad_actuarial: int
    periodo_vigencia: int
    periodo_pago_primas: int
    suma_asegurada: float
    sexo: str
    porcentaje_devolucion: float


class RequestCotizacion(BaseModel):
    producto: str
    parametros: ParametrosCotizacion


@router.get("/endosos/info")
def get_endosos_info_endpoint():
    """
    Endpoint para obtener información del producto endosos
    """
    try:
        info = get_endosos_info()
        return {"success": True, "data": info}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener información: {str(e)}"
        )


@router.get("/vida-cash-plus/info")
def get_vida_cash_plus_info_endpoint():
    """
    Endpoint para obtener información del producto vida cash plus
    """
    try:
        info = get_vida_cash_plus_info()
        return {"success": True, "data": info}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener información: {str(e)}"
        )


@router.get("/info")
def get_all_products_info():
    """
    Endpoint para obtener información de todos los productos disponibles
    """
    try:
        productos_info = {
            "productos_disponibles": [
                {
                    "codigo": Producto.ENDOSOS.value,
                    "nombre": "Endosos",
                    "descripcion": "Producto de seguros de endosos",
                    "endpoint_info": "/api/v1/productos/endosos/info",
                },
                {
                    "codigo": Producto.VIDA_CASH_PLUS.value,
                    "nombre": "Vida Cash Plus",
                    "descripcion": "Producto de seguros Vida Cash Plus",
                    "endpoint_info": "/api/v1/productos/vida-cash-plus/info",
                },
            ],
            "endpoint_cotizacion": "/api/v1/productos/cotizar",
            "version": "1.0.0",
        }
        return {"success": True, "data": productos_info}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al obtener información: {str(e)}"
        )


@router.post("/cotizar")
def cotizar(request: RequestCotizacion):
    """
    Endpoint principal para cotizar productos de seguros
    """
    try:
        producto = request.producto.upper()
        params = request.parametros

        # Validar producto
        productos_soportados = [Producto.ENDOSOS.value, Producto.VIDA_CASH_PLUS.value]
        if producto not in productos_soportados:
            raise HTTPException(
                status_code=400,
                detail=f"Producto no soportado. Productos disponibles: {', '.join(productos_soportados)}",
            )

        # Validar sexo
        if params.sexo.upper() not in ["M", "F"]:
            raise HTTPException(status_code=400, detail="El sexo debe ser 'M' o 'F'")

        # Convertir los parámetros a diccionario para la función de building response
        request_data = {
            "edad_actuarial": params.edad_actuarial,
            "periodo_vigencia": params.periodo_vigencia,
            "periodo_pago_primas": params.periodo_pago_primas,
            "suma_asegurada": params.suma_asegurada,
            "sexo": params.sexo,
            "porcentaje_devolucion": params.porcentaje_devolucion,
        }

        # Usar el orquestador correspondiente según el producto
        if producto == Producto.ENDOSOS.value:
            response_data = cotizar_endosos(request_data)
        elif producto == Producto.VIDA_CASH_PLUS.value:
            response_data = cotizar_vida_cash_plus(request_data)
        else:
            raise HTTPException(
                status_code=400, detail=f"Producto '{producto}' no implementado"
            )

        return {
            "success": True,
            "message": f"Cotización de {producto} realizada exitosamente",
            "data": response_data,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
