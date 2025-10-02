from src.common.constans import VIVOS_INICIO
from src.infrastructure.repositories import get_repos
from src.common.producto import Producto
from src.models.domain.expuestos_mes_domain import ExpuestosMesDomain
from typing import Dict, Any, Optional
from src.utils.anios_meses import anios_meses
import math


class ExpuestosMesService:
    """Servicio para calcular expuestos al mes en seguros de vida"""

    def __init__(
        self,
        producto: Producto,
        periodo_vigencia: int,
        edad_actuarial: int,
        sexo: str,
        fumador: bool,
        cobertura: str,
    ):
        """
        Inicializa el servicio de expuestos al mes

        Args:
            producto: Tipo de producto para cargar la tabla de mortalidad correspondiente
            periodo_vigencia: Período de vigencia del seguro
            edad_actuarial: Edad actuarial del asegurado
            cobertura: Cobertura específica (ej: "fallecimiento", "itp")
        """
        self.producto = producto
        self.periodo_vigencia = periodo_vigencia
        self.edad_actuarial = edad_actuarial
        self.sexo = sexo
        self.fumador = fumador
        self.cobertura = cobertura
        # Obtener repositorios para la cobertura específica
        self.repos = get_repos(producto.value.lower(), cobertura)
        self.tabla_mortalidad = self.repos["tabla_mortalidad"]
        self.caducidad = self.repos["caducidad"]
        self.parametros = self.repos["parametros"]

        # Cargar parámetros una sola vez en el init
        self.parametros_data = self.parametros.get_parametros_by_producto_and_cobertura(
            producto.value.lower(), cobertura
        )

        # Inicializar el dominio
        self.domain = ExpuestosMesDomain()

    def calcular_expuestos_mes(self) -> Dict[int, Dict[str, Any]]:
        """
        Orquesta el cálculo de expuestos al mes usando el dominio

        Returns:
            Diccionario con los resultados mes a mes
        """
        expuestos_mes = {}
        tabla_mortalidad = self.tabla_mortalidad.get_tabla_mortalidad()
        mortalidad_ajuste = self.parametros_data.get("ajuste_mortalidad", 0) / 100
        meses_proyeccion = anios_meses(self.periodo_vigencia)
        vivos_inicio = VIVOS_INICIO
        # Obtener datos de caducidad desde repositorios
        caducidad_parametrizado_mensual = self.caducidad.get_caducidad_mensual_data()
        caducidad_por_año = self.caducidad.get_caducidad_data()

        # Calcular caducidad mensual usando el dominio
        caducidad_mensual = self.domain.calcular_tasa_caducidad_mensual(
            self.periodo_vigencia, caducidad_parametrizado_mensual, caducidad_por_año
        )

        for mes in range(1, meses_proyeccion + 1):
            # Calcular edad actuarial usando el dominio
            edad = self.domain.calcular_edad_actuarial(self.edad_actuarial, mes)

            # Calcular mortalidad usando el dominio
            mortalidad_anual = self.domain.calcular_mortalidad_anual(
                edad, self.sexo, self.fumador, tabla_mortalidad
            )
            mortalidad_mensual = self.domain.calcular_mortalidad_mensual(
                mortalidad_anual
            )
            mortalidad_ajustada = self.domain.calcular_mortalidad_ajustada(
                mortalidad_mensual, mortalidad_ajuste
            )

            # Calcular fallecidos y supervivientes usando el dominio
            fallecidos = self.domain.calcular_fallecidos(
                vivos_inicio, mortalidad_ajustada
            )
            vivos_despues_fallecidos = self.domain.calcular_vivos_despues_fallecidos(
                vivos_inicio, fallecidos
            )

            # Calcular caducados usando el dominio
            caducados = self.domain.calcular_caducados(
                vivos_despues_fallecidos, caducidad_mensual[mes]
            )
            vivos_final = self.domain.calcular_vivos_finales(
                vivos_despues_fallecidos, caducados
            )

            # Estructurar resultado
            expuestos_mes[mes] = {
                "caducidad_mensual": caducidad_mensual[mes],
                "mortalidad_anual": mortalidad_anual,
                "mortalidad_mensual": mortalidad_mensual,
                "mortalidad_ajustada": mortalidad_ajustada,
                "mortalidad_ajuste": mortalidad_ajuste,
                "vivos_inicio": vivos_inicio,
                "fallecidos": fallecidos,
                "vivos_despues_fallecidos": vivos_despues_fallecidos,
                "caducados": caducados,
                "vivos_final": vivos_final,
            }

            # Actualizar vivos para el siguiente mes
            vivos_inicio = vivos_final

        return expuestos_mes
