# Cotizador VidaCash

API para cotización de seguros de vida desarrollada con FastAPI.

## 🏗️ Arquitectura

```
cotizador-vidacash/
├── src/
│   ├── api/                    # Capa de API
│   │   ├── routes/            # Routers de endpoints
│   │   │   ├── __init__.py
│   │   │   └── cotizacion_router.py
│   │   └── __init__.py
│   ├── domain/                # Lógica de negocio
│   │   └── services/
│   ├── infrastructure/        # Acceso a datos
│   │   └── repositories/      # Repositorios de datos
│   │       ├── __init__.py
│   │       ├── repos.py       # Acceso simple por producto/cobertura
│   │       ├── caducidad_repository.py
│   │       ├── devolucion_repository.py
│   │       ├── parametros_repository.py
│   │       ├── tabla_mortalidad_repository.py
│   │       ├── tasa_interes_repository.py
│   │       ├── tarifas_reaseguro.py
│   │       ├── factores_pago_repository.py
│   │       └── periodos_cotizacion_repository.py
│   └── interfaces/            # Interfaces externas
├── assets/                    # Datos estáticos
│   └── productos/
│       └── endosos/
│           └── coberturas/
│               ├── fallecimiento/
│               └── itp/
├── main.py                   # Aplicación principal
├── test_cotizacion.py        # Script de pruebas
└── README.md
```

## 🚀 Instalación y Ejecución

### 1. Instalar dependencias
```bash
pip install fastapi uvicorn requests
```

### 2. Ejecutar el servidor
```bash
python main.py
```

El servidor se ejecutará en: `http://0.0.0.0:8081`

### 3. Probar la API
```bash
python test_cotizacion.py
```

## 📡 Endpoints

### Health Check
```
GET /health
```

### Cotización
```
POST /api/v1/productos/cotizar
```

**Body:**
```json
{
    "producto": "ENDOSOS",
    "parametros": {
        "edad_actuarial": 28,
        "periodo_vigencia": 15,
        "periodo_pago_primas": 15,
        "suma_asegurada": 200000,
        "sexo": "M",
        "porcentaje_devolucion": 125
    }
}
```

## 🔧 Uso de Repositorios

### Acceso Simple
```python
from src.infrastructure.repositories import get_fallecimiento_repos, get_itp_repos, get_repos

# Para fallecimiento
fallecimiento = get_fallecimiento_repos()
caducidad = fallecimiento["caducidad"]

# Para ITP
itp = get_itp_repos()
tarifas = itp["tarifas_reaseguro"]

# Para cualquier producto/cobertura
mis_repos = get_repos("endosos", "fallecimiento")
```

## 📊 Documentación

- **Swagger UI**: `http://0.0.0.0:8081/docs`
- **ReDoc**: `http://0.0.0.0:8081/redoc`

## 🗂️ Estructura de Datos

Los datos se organizan por:
- **Producto**: `endosos`
- **Coberturas**: `fallecimiento`, `itp`
- **Archivos**: `caducidad.json`, `devolucion.json`, `parametros.json`, etc.

Ruta: `assets/productos/{producto}/coberturas/{cobertura}/`
