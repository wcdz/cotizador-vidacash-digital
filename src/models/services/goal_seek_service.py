from typing import Dict, Any
from src.models.services.calculo_actuarial_service import CalculoActuarialService
from src.common.producto import Producto


class GoalSeekService:
    """
    Servicio que implementa Goal Seek para encontrar el valor de prima_asignada
    que hace que el VNA se acerque más a cero.
    """
    
    def __init__(self):
        self.tolerance = 1e-6  # Tolerancia para convergencia (máxima precisión)
        self.max_iterations = 100  # Máximo número de iteraciones
        self.min_prima = 0.01  # Prima mínima
        self.max_prima = 10000.0  # Prima máxima (ajustar según necesidad)
    
    def execute(
        self, 
        parametros_entrada: Dict[str, Any], 
        parametros_almacenados: Dict[str, Any], 
        parametros_calculados: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ejecuta el Goal Seek para encontrar la prima_asignada óptima.
        
        Args:
            parametros_entrada: Parámetros de entrada del usuario
            parametros_almacenados: Parámetros almacenados
            parametros_calculados: Parámetros calculados
            
        Returns:
            Diccionario con la prima_asignada óptima y el VNA resultante
        """
        try:
            # Obtener coberturas activas
            coberturas_obj = parametros_entrada.get("coberturas", {})
            if isinstance(coberturas_obj, dict):
                coberturas = [k for k, v in coberturas_obj.items() if v]
            else:
                coberturas = coberturas_obj if isinstance(coberturas_obj, list) else []
            
            if not coberturas:
                return {"error": "No hay coberturas activas"}
            
            # Obtener parámetros necesarios
            sexo = parametros_entrada.get("sexo", "M")
            fumador = parametros_entrada.get("fumador", False)
            
            # Optimizar cada cobertura independientemente
            resultados_por_cobertura = {}
            
            for cobertura in coberturas:
                print(f"\n🎯 Optimizando cobertura: {cobertura.upper()}")
                print("=" * 50)
                
                # Realizar Goal Seek para esta cobertura
                prima_optima, vna_resultado = self._goal_seek_bisection(
                    parametros_entrada,
                    parametros_almacenados,
                    parametros_calculados,
                    cobertura,
                    sexo,
                    fumador
                )
                
                # Guardar resultado para esta cobertura
                resultados_por_cobertura[cobertura] = {
                    "prima_asignada_optima": prima_optima,
                    "vna_resultado": vna_resultado,
                    "iteraciones": getattr(self, '_iterations', 0),
                    "convergio": abs(vna_resultado) < self.tolerance
                }
                
                print(f"✅ {cobertura.upper()} optimizada:")
                print(f"   Prima óptima: {prima_optima:.6f}")
                print(f"   VNA resultante: {vna_resultado:.12f}")
                print(f"   Convergió: {abs(vna_resultado) < self.tolerance}")
                print(f"   Iteraciones: {getattr(self, '_iterations', 0)}")
            
            return {
                "coberturas_optimizadas": resultados_por_cobertura,
                "total_coberturas": len(coberturas),
                "coberturas_procesadas": list(coberturas)
            }
            
        except Exception as e:
            return {
                "error": f"Error en Goal Seek: {str(e)}",
                "prima_asignada_optima": None,
                "vna_resultado": None
            }
    
    def _goal_seek_bisection(
        self,
        parametros_entrada: Dict[str, Any],
        parametros_almacenados: Dict[str, Any],
        parametros_calculados: Dict[str, Any],
        cobertura: str,
        sexo: str,
        fumador: bool
    ) -> tuple[float, float]:
        """
        Implementa Goal Seek usando el método de bisección.
        
        Returns:
            Tupla con (prima_optima, vna_resultado)
        """
        # Crear copias de los parámetros para no modificar los originales
        parametros_almacenados_copy = self._deep_copy_params(parametros_almacenados)
        
        # Empezar siempre desde 0 para encontrar la prima óptima real
        prima_inicial = 0.0
        
        # Calcular VNA inicial con prima = 0
        vna_inicial = self._calcular_vna_con_prima(
            parametros_entrada,
            parametros_almacenados_copy,
            parametros_calculados,
            cobertura,
            sexo,
            fumador,
            prima_inicial
        )
        
        print(f"VNA con prima = 0: {vna_inicial}")
        
        # Si ya está cerca de cero con prima = 0, retornar
        if abs(vna_inicial) < self.tolerance:
            return prima_inicial, vna_inicial
        
        # Determinar el rango de búsqueda
        if vna_inicial > 0:
            # VNA positivo con prima=0, necesitamos disminuir la prima (imposible, usar rango fijo)
            prima_low = self.min_prima
            prima_high = 1000.0  # Rango fijo para explorar
        else:
            # VNA negativo con prima=0, necesitamos AUMENTAR la prima
            prima_low = prima_inicial  # 0.0
            prima_high = self.max_prima  # 10000.0
        
        # Verificar que tenemos un cambio de signo
        vna_low = self._calcular_vna_con_prima(
            parametros_entrada, parametros_almacenados_copy, parametros_calculados,
            cobertura, sexo, fumador, prima_low
        )
        vna_high = self._calcular_vna_con_prima(
            parametros_entrada, parametros_almacenados_copy, parametros_calculados,
            cobertura, sexo, fumador, prima_high
        )
        
        if vna_low * vna_high > 0:
            # No hay cambio de signo, expandir el rango
            print(f"No hay cambio de signo inicial. VNA_low={vna_low}, VNA_high={vna_high}")
            
            if vna_low > 0:
                # VNA positivo, buscar hacia abajo
                print("Buscando cambio de signo hacia primas menores...")
                prima_high = prima_low * 2
                while prima_high < self.max_prima:
                    vna_high = self._calcular_vna_con_prima(
                        parametros_entrada, parametros_almacenados_copy, parametros_calculados,
                        cobertura, sexo, fumador, prima_high
                    )
                    print(f"Probando prima_high={prima_high}, VNA={vna_high}")
                    if vna_high < 0:
                        break
                    prima_high *= 2
            else:
                # VNA negativo, buscar hacia arriba
                print("Buscando cambio de signo hacia primas mayores...")
                prima_high = prima_low * 2
                while prima_high < self.max_prima:
                    vna_high = self._calcular_vna_con_prima(
                        parametros_entrada, parametros_almacenados_copy, parametros_calculados,
                        cobertura, sexo, fumador, prima_high
                    )
                    print(f"Probando prima_high={prima_high}, VNA={vna_high}")
                    if vna_high > 0:
                        break
                    prima_high *= 2
        
        # Bisección
        self._iterations = 0
        print(f"Iniciando búsqueda entre prima_low={prima_low} y prima_high={prima_high}")
        print(f"VNA_low={vna_low}, VNA_high={vna_high}")
        
        for i in range(self.max_iterations):
            self._iterations = i + 1
            
            prima_media = (prima_low + prima_high) / 2
            vna_media = self._calcular_vna_con_prima(
                parametros_entrada, parametros_almacenados_copy, parametros_calculados,
                cobertura, sexo, fumador, prima_media
            )
            
            print(f"Iteración {i+1}: prima={prima_media:.6f}, VNA={vna_media:.12f}")
            
            if abs(vna_media) < self.tolerance:
                print(f"¡Convergencia alcanzada! VNA={vna_media:.12f} < tolerancia={self.tolerance}")
                return prima_media, vna_media
            
            if vna_media * vna_low < 0:
                prima_high = prima_media
                vna_high = vna_media
                print(f"  -> Nueva prima_high={prima_high}")
            else:
                prima_low = prima_media
                vna_low = vna_media
                print(f"  -> Nueva prima_low={prima_low}")
            
            # Verificar convergencia
            if abs(prima_high - prima_low) < self.tolerance:
                print(f"Convergencia por rango: |{prima_high} - {prima_low}| < {self.tolerance}")
                break
        
        # Retornar la mejor aproximación
        prima_final = (prima_low + prima_high) / 2
        vna_final = self._calcular_vna_con_prima(
            parametros_entrada, parametros_almacenados_copy, parametros_calculados,
            cobertura, sexo, fumador, prima_final
        )
        
        return prima_final, vna_final
    
    def _calcular_vna_con_prima(
        self,
        parametros_entrada: Dict[str, Any],
        parametros_almacenados: Dict[str, Any],
        parametros_calculados: Dict[str, Any],
        cobertura: str,
        sexo: str,
        fumador: bool,
        prima_asignada: float
    ) -> float:
        """
        Calcula el VNA con una prima_asignada específica.
        
        Args:
            prima_asignada: Valor de prima a probar
            
        Returns:
            VNA calculado
        """
        try:
            # Actualizar la prima en los parámetros almacenados
            parametros_almacenados["coberturas"][cobertura]["prima_asignada"] = prima_asignada
            
            # Crear instancia del servicio de cálculo actuarial
            calculo_service = CalculoActuarialService(
                parametros_entrada=parametros_entrada,
                parametros_almacenados=parametros_almacenados,
                parametros_calculados=parametros_calculados,
                producto=Producto.ENDOSOS,
                sexo=sexo,
                fumador=fumador,
                cobertura=cobertura
            )
            
            # Ejecutar el cálculo y obtener el VNA
            vna = calculo_service.execute()
            
            return vna
            
        except Exception as e:
            print(f"Error calculando VNA con prima {prima_asignada}: {e}")
            return float('inf')  # Retornar un valor muy grande para indicar error
    
    def _deep_copy_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza una copia profunda de los parámetros para no modificar los originales.
        """
        import copy
        return copy.deepcopy(params)
