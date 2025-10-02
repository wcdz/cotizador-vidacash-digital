"""
API principal del Cotizador VidaCash
"""

from fastapi import FastAPI
from src.interfaces.api.routes import cotizacion_router

app = FastAPI(
    title="Cotizador VidaCash",
    version="1.0.0",
    description="API para cotización de seguros de vida",
)

# Incluir routers
app.include_router(cotizacion_router)


@app.get("/")
def read_root():
    return {
        "message": "API del Cotizador VidaCash",
        "version": "1.0.0",
        "endpoints": {
            "cotizacion": "/api/v1/productos/cotizar",
            "docs": "/docs",
            "redoc": "/redoc",
        },
    }


@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "cotizador-vidacash"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8081)
