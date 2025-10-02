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
def get_info():
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


@router.post("/cotizar")
def cotizar(request: RequestCotizacion):
    """
    Endpoint principal para cotizar productos de seguros
    """
    try:
        producto = request.producto.upper()
        params = request.parametros

        # Validar producto
        if producto != "ENDOSOS":
            raise HTTPException(
                status_code=400, detail="Solo se soporta el producto ENDOSOS"
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

        # Usar el orquestador de endosos para generar la respuesta completa
        response_data = cotizar_endosos(request_data)

        return {
            "success": True,
            "message": "Cotización realizada exitosamente",
            "data": response_data,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
