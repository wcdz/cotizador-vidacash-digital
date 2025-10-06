"""
Orquestador principal para el producto ENDOSOS
"""

from typing import Dict, Any, List
from src.models.productos.endosos.core.parameter_loading_step import (
    ParameterLoadingStep,
)
from src.models.productos.endosos.core.response_building_step import (
    build_endosos_response,
    _get_default_endosos_values,
    _load_parametros_almacenados_por_cobertura,
)
from src.infrastructure.repositories.repos import get_repos
from src.models.domain.parametros_calculados import ParametrosCalculados
from src.models.services.parametros_calculados_service import (
    ParametrosCalculadosService,
)
from src.models.productos.endosos.coberturas.fallecimiento import FallecimientoCobertura
from src.models.productos.endosos.coberturas.itp import ItpCobertura
from src.common.producto import Producto
from src.models.services.calculo_actuarial_service import CalculoActuarialService


class EndososOrchestrator:
    """
    Orquestador principal para el producto ENDOSOS.
    Coordina la carga de parámetros y construcción de respuestas.
    """

    def __init__(self):
        self.producto = "endosos"
        self._coberturas_disponibles = None
        self._parametros_calculados = ParametrosCalculados()
        self._parametros_calculados_service = ParametrosCalculadosService()
        self._cobertura_fallecimiento = FallecimientoCobertura()
        self._cobertura_itp = ItpCobertura()

    def _cargar_coberturas_disponibles(self) -> List[str]:
        """
        Carga las coberturas disponibles desde el repositorio

        Returns:
            Lista de coberturas disponibles para el producto
        """
        if self._coberturas_disponibles is None:
            try:
                repos = get_repos(self.producto)
                coberturas_repo = repos["coberturas"]
                self._coberturas_disponibles = (
                    coberturas_repo.get_coberturas_by_producto(self.producto)
                )
                print(
                    f"Coberturas cargadas para {self.producto}: {self._coberturas_disponibles}"
                )
            except Exception as e:
                print(f"Error al cargar coberturas: {e}")
                # Fallback a coberturas por defecto
                self._coberturas_disponibles = ["fallecimiento", "itp"]

        return self._coberturas_disponibles

    def cotizar(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Método principal para realizar cotizaciones de endosos

        Args:
            request_data: Datos de la petición de cotización

        Returns:
            Diccionario con la respuesta completa de cotización
        """
        try:
            # 1. Preparar parámetros de entrada
            parametros_entrada = self._preparar_parametros_entrada(request_data)

            # 2. Cargar parámetros almacenados por cobertura
            parametros_almacenados = self._cargar_parametros_almacenados(
                parametros_entrada
            )

            # 3. Calcular parámetros específicos
            parametros_calculados = self._calcular_parametros_calculados(
                parametros_entrada, parametros_almacenados
            )

            # 4. Calcular datos específicos de endosos (mantener para pruebas)
            """calcular_endosos = self._calcular_endosos(
                parametros_entrada, parametros_almacenados, parametros_calculados
            )"""

            # 5. Ejecutar cálculos actuariales con Goal Seek por cobertura
            calcular_goalseek = self._calcular_goalseek(
                parametros_entrada, parametros_almacenados, parametros_calculados
            )

            calcular_tabla_devolucion = self._calcular_tabla_devolucion(
                parametros_entrada
            )

            # 6. Preparar respuesta
            endosos = self._preparar_respuesta(
                calcular_goalseek, parametros_entrada, calcular_tabla_devolucion
            )

            # 6. Construir respuesta final
            response = build_endosos_response(
                parametros_entrada=parametros_entrada,
                parametros_almacenados=parametros_almacenados,
                parametros_calculados=parametros_calculados,
                endosos=endosos,
            )

            return response

        except Exception as e:
            print(f"Error en orquestación de endosos: {e}")
            print(f"Tipo de error: {type(e).__name__}")
            raise

    def _preparar_parametros_entrada(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepara los parámetros de entrada combinando request_data con valores por defecto

        Args:
            request_data: Datos de la petición

        Returns:
            Parámetros de entrada preparados en el orden especificado
        """
        # Obtener valores por defecto
        valores_default = _get_default_endosos_values()

        # Definir el orden específico de los parámetros
        orden_parametros = [
            "edad_actuarial",
            "moneda",
            "periodo_vigencia",
            "periodo_pago_primas",
            "suma_asegurada",
            "sexo",
            "frecuencia_pago_primas",
            "fumador",
            "asistencia",
            "porcentaje_devolucion",
            "coberturas",
        ]

        # Crear diccionario ordenado
        parametros_entrada = {}

        for param in orden_parametros:
            if param in request_data and request_data[param] is not None:
                # Usar valor de la petición si existe y no es None
                parametros_entrada[param] = request_data[param]
            elif param in valores_default:
                # Usar valor por defecto
                parametros_entrada[param] = valores_default[param]

        # Procesar coberturas específicamente
        if "coberturas" in parametros_entrada:
            coberturas = parametros_entrada["coberturas"]
            if isinstance(coberturas, list):
                # Cargar coberturas disponibles dinámicamente
                coberturas_disponibles = self._cargar_coberturas_disponibles()

                # Convertir array a objeto con claves ordenadas según coberturas disponibles
                coberturas_obj = {}
                for cobertura in coberturas_disponibles:
                    coberturas_obj[cobertura] = cobertura in coberturas

                parametros_entrada["coberturas"] = coberturas_obj

        return parametros_entrada

    def _cargar_parametros_almacenados(
        self, parametros_entrada: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Carga los parámetros almacenados para las coberturas especificadas

        Args:
            parametros_entrada: Parámetros de entrada

        Returns:
            Parámetros almacenados organizados por cobertura
        """
        # Obtener coberturas del nuevo formato
        coberturas_obj = parametros_entrada.get("coberturas", {})

        if isinstance(coberturas_obj, dict):
            # Nuevo formato: {"itp": true, "fallecimiento": true}
            coberturas = [k for k, v in coberturas_obj.items() if v]
        else:
            # Formato legacy: ["itp", "fallecimiento"]
            coberturas = (
                coberturas_obj
                if isinstance(coberturas_obj, list)
                else self._cargar_coberturas_disponibles()
            )

        return _load_parametros_almacenados_por_cobertura(coberturas)

    def _calcular_parametros_calculados(
        self, parametros_entrada: Dict[str, Any], parametros_almacenados: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calcula parámetros específicos basados en los parámetros de entrada y almacenados

        Args:
            parametros_entrada: Parámetros de entrada
            parametros_almacenados: Parámetros almacenados

        Returns:
            Parámetros calculados
        """
        # Cargar datos necesarios para los cálculos (solo los específicos de endosos)
        tasas_interes_data = self._cargar_tasas_interes_por_cobertura(
            parametros_almacenados
        )

        # Obtener coberturas del nuevo formato
        coberturas_obj = parametros_entrada.get("coberturas", {})

        # Calcular parámetros calculados por cobertura usando el servicio centralizado
        parametros_calculados_por_cobertura = {}

        for cobertura, parametros in parametros_almacenados["coberturas"].items():
            try:
                if cobertura == "fallecimiento":
                    self._cobertura_fallecimiento.parametros = parametros
                    parametros_calculados_por_cobertura[cobertura] = (
                        self._cobertura_fallecimiento.calcular_parametros_calculados(
                            parametros_entrada, tasas_interes_data, Producto.ENDOSOS
                        )
                    )

                elif cobertura == "itp":
                    self._cobertura_itp.parametros = parametros
                    parametros_calculados_por_cobertura[cobertura] = (
                        self._cobertura_itp.calcular_parametros_calculados(
                            parametros_entrada, tasas_interes_data, Producto.ENDOSOS
                        )
                    )
                print("\n")
            except Exception as e:
                print(f"Error en cobertura '{cobertura}': {e}")
                raise Exception(f"Error en cobertura '{cobertura}': {e}") from e

        # Usar los parámetros calculados por cobertura que ya calculamos arriba
        parametros_calculados = {"coberturas": parametros_calculados_por_cobertura}

        return parametros_calculados

    def _cargar_tasas_interes_por_cobertura(
        self, parametros_almacenados: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Carga las tasas de interés desde la primera cobertura disponible"""
        try:
            # Obtener la primera cobertura disponible
            coberturas = parametros_almacenados.get("coberturas", {})
            if not coberturas:
                print("DEBUG - No hay coberturas disponibles")
                return {}

            primera_cobertura = list(coberturas.keys())[0]
            # Cargar tasas de interés desde la cobertura específica
            repos = get_repos(self.producto, primera_cobertura)
            tasa_interes_repo = repos.get("tasa_interes")
            if tasa_interes_repo:
                tasas_interes_raw = tasa_interes_repo.get_tasas_interes()
                # Procesar las tasas con el helper para agregar tasa_reserva
                from src.helpers.tasa_interes_reserva import tasa_interes_reserva

                tasas_procesadas = tasa_interes_reserva(tasas_interes_raw)
                return tasas_procesadas
            else:
                print(
                    f"DEBUG - No se encontró repositorio de tasas de interés para {primera_cobertura}"
                )
                return {}
        except Exception as e:
            print(f"Error al cargar tasas de interés por cobertura: {e}")
            return {}

    def _cargar_tasas_interes(self) -> Dict[str, Any]:
        """Carga las tasas de interés desde el repositorio y las procesa"""
        try:
            repos = get_repos(self.producto)
            tasa_interes_repo = repos.get("tasa_interes")
            if tasa_interes_repo:
                tasas_interes_raw = tasa_interes_repo.get_tasas_interes()
                print(f"DEBUG - Tasas de interés RAW: {tasas_interes_raw}")

                # Procesar las tasas con el helper para agregar tasa_reserva
                from src.helpers.tasa_interes_reserva import tasa_interes_reserva

                tasas_procesadas = tasa_interes_reserva(tasas_interes_raw)
                return tasas_procesadas
            else:
                print("DEBUG - No se encontró repositorio de tasas de interés")
                return {}
        except Exception as e:
            print(f"Error al cargar tasas de interés: {e}")
            return {}

    def _calcular_endosos(
        self,
        parametros_entrada: Dict[str, Any],
        parametros_almacenados: Dict[str, Any],
        parametros_calculados: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Calcula los datos específicos de endosos

        Args:
            parametros_entrada: Parámetros de entrada
            parametros_almacenados: Parámetros almacenados
            parametros_calculados: Parámetros calculados

        Returns:
            Datos específicos de endosos
        """
        # Obtener coberturas del nuevo formato
        coberturas_obj = parametros_entrada.get("coberturas", {})

        # Determinar coberturas activas
        if isinstance(coberturas_obj, dict):
            # Nuevo formato: {"itp": true, "fallecimiento": true}
            coberturas = [k for k, v in coberturas_obj.items() if v]
        else:
            # Formato legacy: ["itp", "fallecimiento"]
            coberturas = (
                coberturas_obj
                if isinstance(coberturas_obj, list)
                else self._cargar_coberturas_disponibles()
            )

        # Ejecutar cálculos actuariales usando instancias independientes de cada cobertura
        resultados_actuariales = {}

        if "fallecimiento" in coberturas:
            fallecimiento_cobertura = FallecimientoCobertura()
            resultados_fallecimiento = fallecimiento_cobertura.calculo_actuarial(
                parametros_entrada, parametros_almacenados, parametros_calculados
            )
            # print(f"Resultados actuariales FALLECIMIENTO: {resultados_fallecimiento}")

        if "itp" in coberturas:
            itp_cobertura = ItpCobertura()
            resultados_itp = itp_cobertura.calculo_actuarial(
                parametros_entrada, parametros_almacenados, parametros_calculados
            )
            # print(f"Resultados actuariales ITP: {resultados_itp}")

        endosos_data = {
            "coberturas": {},
            "tabla_devolucion": "",
            "calculado_por": "EndososOrchestrator",
        }

        # Ordenar coberturas según el orden específico
        orden_coberturas = ["fallecimiento", "itp"]
        coberturas_ordenadas = []
        for cobertura in orden_coberturas:
            if cobertura in coberturas:
                coberturas_ordenadas.append(cobertura)
        for cobertura in coberturas:
            if cobertura not in coberturas_ordenadas:
                coberturas_ordenadas.append(cobertura)

        for cobertura in coberturas_ordenadas:
            # Aquí se implementarían los cálculos específicos de endosos por cobertura
            # Por ahora, inicializamos con estructura vacía
            endosos_data["coberturas"][cobertura] = {
                "calculado_por": "EndososOrchestrator",
                "cobertura": cobertura,
            }

        return endosos_data

    def _calcular_tabla_devolucion(
        self,
        parametros_entrada: Dict[str, Any],
    ) -> list:
        """
        Calcula la tabla de devoluciones usando el servicio de parámetros calculados
        """
        periodo_vigencia = parametros_entrada["periodo_vigencia"]
        porcentaje_devolucion = parametros_entrada["porcentaje_devolucion"]

        return str(
            self._parametros_calculados_service.calcular_tabla_devolucion_completa(
                periodo_vigencia=periodo_vigencia,
                porcentaje_devolucion=porcentaje_devolucion,
                producto="endosos",
                cobertura="fallecimiento",
            )
        )

    def _calcular_goalseek(
        self,
        parametros_entrada: Dict[str, Any],
        parametros_almacenados: Dict[str, Any],
        parametros_calculados: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Ejecuta cálculos actuariales con Goal Seek para todas las coberturas activas

        Args:
            parametros_entrada: Parámetros de entrada del usuario
            parametros_almacenados: Parámetros almacenados
            parametros_calculados: Parámetros calculados

        Returns:
            Diccionario con resultados de Goal Seek por cobertura
        """
        try:
            # Obtener coberturas activas
            coberturas_obj = parametros_entrada.get("coberturas", {})
            if isinstance(coberturas_obj, dict):
                coberturas = [k for k, v in coberturas_obj.items() if v]
            else:
                coberturas = coberturas_obj if isinstance(coberturas_obj, list) else []

            # Ejecutar cálculos actuariales con Goal Seek para cada cobertura
            resultados_por_cobertura = {}

            if "fallecimiento" in coberturas:
                print(f"\n🎯 Procesando FALLECIMIENTO con Goal Seek...")
                fallecimiento_cobertura = FallecimientoCobertura()
                resultados_fallecimiento = (
                    fallecimiento_cobertura.calculo_actuarial_con_goal_seek(
                        parametros_entrada,
                        parametros_almacenados,
                        parametros_calculados,
                    )
                )
                resultados_por_cobertura["fallecimiento"] = resultados_fallecimiento

            if "itp" in coberturas:
                print(f"\n🎯 Procesando ITP con Goal Seek...")
                itp_cobertura = ItpCobertura()
                resultados_itp = itp_cobertura.calculo_actuarial_con_goal_seek(
                    parametros_entrada, parametros_almacenados, parametros_calculados
                )
                resultados_por_cobertura["itp"] = resultados_itp

            print(
                f"\n✅ Total de coberturas procesadas: {len(resultados_por_cobertura)}"
            )

            return resultados_por_cobertura

        except Exception as e:
            print(f"Error en cálculo de Goal Seek: {e}")
            return {}

    def _preparar_respuesta(
        self,
        calcular_goalseek: Dict[str, Any],
        parametros_entrada: Dict[str, Any],
        tabla_devolucion: Any = None,
    ) -> Dict[str, Any]:
        """
        Prepara la respuesta final usando los métodos preparar_respuesta de cada cobertura
        """
        try:
            print(f"\n🔧 Preparando respuesta estructurada...")
            print(f"Coberturas a procesar: {list(calcular_goalseek.keys())}")

            primas_coberturas = {}

            # Procesar cada cobertura que fue calculada
            for cobertura, resultados in calcular_goalseek.items():
                print(f"Procesando cobertura: {cobertura}")

                if cobertura == "fallecimiento":
                    fallecimiento_cobertura = FallecimientoCobertura()
                    respuesta_estructurada = fallecimiento_cobertura.preparar_respuesta(
                        resultados, parametros_entrada
                    )
                    primas_coberturas[cobertura] = respuesta_estructurada
                    print(
                        f"✅ Fallecimiento estructurado: {list(respuesta_estructurada.keys())}"
                    )

                elif cobertura == "itp":
                    itp_cobertura = ItpCobertura()
                    respuesta_estructurada = itp_cobertura.preparar_respuesta(
                        resultados, parametros_entrada
                    )
                    primas_coberturas[cobertura] = respuesta_estructurada
                    print(f"✅ ITP estructurado: {list(respuesta_estructurada.keys())}")

                else:
                    # Para primas_coberturas no reconocidas, usar la respuesta tal como viene
                    primas_coberturas[cobertura] = resultados
                    print(
                        f"⚠️ Cobertura no reconocida {cobertura}, usando respuesta original"
                    )

            primas_cliente = self._calcular_primas_cliente(primas_coberturas)
            # Estructurar la respuesta con coberturas anidadas
            respuesta_final = {
                "coberturas": primas_coberturas,
                "primas_cliente": primas_cliente,
            }

            # Agregar tabla de devolución si está disponible
            if tabla_devolucion is not None:
                respuesta_final["tabla_devolucion"] = tabla_devolucion
                print(f"✅ Tabla de devolución agregada: {tabla_devolucion}")

            print(
                f"🎉 Respuesta final preparada con {len(primas_coberturas)} coberturas"
            )
            return respuesta_final

        except Exception as e:
            print(f"❌ Error preparando respuesta: {e}")
            print(f"Tipo de error: {type(e).__name__}")
            import traceback

            traceback.print_exc()
            # En caso de error, retornar los resultados originales con estructura correcta
            return {"coberturas": calcular_goalseek}

    def _calcular_primas_cliente(self, primas_coberturas):
        """
        Suma los valores de cada clave entre todas las coberturas
        """
        try:
            print(f"\n🧮 Calculando primas del cliente sumando coberturas...")

            if not primas_coberturas:
                return {}

            # Obtener estructura de referencia de la primera cobertura
            primera_cobertura = next(iter(primas_coberturas.values()))

            primas_cliente = {}

            # Procesar cada clave principal
            for clave, estructura_referencia in primera_cobertura.items():
                primas_cliente[clave] = {}

                # Procesar cada subclave (mensual, trimestral, etc.)
                for subclave in estructura_referencia.keys():
                    suma_total = sum(
                        cobertura_datos[clave][subclave]
                        for cobertura_datos in primas_coberturas.values()
                        if clave in cobertura_datos
                        and subclave in cobertura_datos[clave]
                    )

                    primas_cliente[clave][subclave] = suma_total
                    print(f"  {clave}.{subclave}: {suma_total}")

            print(f"✅ Primas del cliente calculadas exitosamente")
            return primas_cliente

        except Exception as e:
            print(f"❌ Error calculando primas del cliente: {e}")
            import traceback

            traceback.print_exc()
            return {}

    def get_cobertura_info(self, cobertura: str) -> Dict[str, Any]:
        """
        Obtiene información específica de una cobertura

        Args:
            cobertura: Nombre de la cobertura

        Returns:
            Información de la cobertura
        """
        if cobertura not in self._cargar_coberturas_disponibles():
            raise ValueError(f"Cobertura '{cobertura}' no soportada")

        # Cargar parámetros de la cobertura específica
        step = ParameterLoadingStep(self.producto, cobertura)
        parametros = step.execute()

        return {
            "cobertura": cobertura,
            "parametros": parametros,
            "parametros_disponibles": step.get_parametros_disponibles(),
            "es_fallecimiento": step.es_fallecimiento(),
            "es_itp": step.es_itp(),
        }

    def get_coberturas_disponibles(self) -> List[str]:
        """
        Obtiene la lista de coberturas disponibles

        Returns:
            Lista de coberturas disponibles
        """
        return self._cargar_coberturas_disponibles().copy()


# Instancia global del orquestador
endosos_orchestrator = EndososOrchestrator()


# Funciones de conveniencia para mantener compatibilidad
def cotizar_endosos(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Función de conveniencia para cotizar endosos

    Args:
        request_data: Datos de la petición

    Returns:
        Respuesta de cotización
    """
    return endosos_orchestrator.cotizar(request_data)


def get_endosos_info() -> Dict[str, Any]:
    """
    Obtiene información general del producto endosos

    Returns:
        Información del producto
    """
    return {
        "producto": "endosos",
        "coberturas_disponibles": endosos_orchestrator.get_coberturas_disponibles(),
        "descripcion": "Producto de seguros de endosos",
        "version": "1.0.0",
    }
