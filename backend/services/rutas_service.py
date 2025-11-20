"""
Servicio para optimización de rutas usando Google Maps Directions API
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from models.pedido import Pedido
from config.rutas_config import PUNTO_INICIO, HORA_INICIO_DEFAULT, TIEMPO_ENTREGA_PROMEDIO


class RutasService:
    """Servicio para optimizar rutas de entrega"""

    @staticmethod
    def _get_google_api_key() -> Optional[str]:
        """Obtiene la API key de Google Maps desde variables de entorno"""
        return os.getenv('GOOGLE_MAPS_API_KEY')

    @staticmethod
    def _geocodificar_direccion(direccion: str, comuna: str = None) -> Optional[Tuple[float, float]]:
        """
        Geocodifica una dirección usando Google Maps Geocoding API
        Retorna (latitud, longitud) o None si falla
        
        Args:
            direccion: Dirección completa
            comuna: Comuna (opcional, para mejorar precisión)
        """
        api_key = RutasService._get_google_api_key()
        if not api_key:
            return None
        
        try:
            # Construir dirección completa
            direccion_completa = direccion
            if comuna:
                direccion_completa += f", {comuna}, Chile"
            else:
                direccion_completa += ", Chile"
            
            # Llamar a Geocoding API
            url = "https://maps.googleapis.com/maps/api/geocode/json"
            params = {
                'address': direccion_completa,
                'key': api_key,
                'region': 'cl',  # Priorizar resultados en Chile
                'language': 'es'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'OK' and data.get('results'):
                location = data['results'][0]['geometry']['location']
                return (location['lat'], location['lng'])
            else:
                return None

        except Exception as e:
            return None

    @staticmethod
    def _calcular_distancia_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calcula la distancia en línea recta entre dos puntos GPS usando la fórmula de Haversine
        Retorna distancia en kilómetros
        """
        from math import radians, cos, sin, asin, sqrt

        # Convertir a radianes
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

        # Fórmula de Haversine
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))

        # Radio de la Tierra en km
        r = 6371

        return c * r

    @staticmethod
    def optimizar_ruta_simple(pedidos: List[Pedido], hora_inicio: str = HORA_INICIO_DEFAULT) -> List[Dict]:
        """
        Optimiza ruta usando algoritmo greedy (vecino más cercano)
        No requiere API de Google, usa coordenadas GPS directamente

        Args:
            pedidos: Lista de pedidos a optimizar
            hora_inicio: Hora de inicio de la ruta (formato HH:MM)
        """
        if not pedidos:
            return []

        # Filtrar pedidos que tienen coordenadas
        pedidos_con_coords = [p for p in pedidos if p.latitud and p.longitud]

        if not pedidos_con_coords:
            # Si no hay coordenadas, retornar en orden de hora de entrega
            return [{
                'pedido_id': p.id,
                'orden': idx + 1,
                'distancia_km': None,
                'tiempo_estimado_min': None
            } for idx, p in enumerate(sorted(pedidos, key=lambda x: x.fecha_entrega))]

        # Punto actual (inicio)
        lat_actual = PUNTO_INICIO['latitud']
        lon_actual = PUNTO_INICIO['longitud']

        # Parsear hora de inicio
        hora_inicio_dt = datetime.strptime(hora_inicio, '%H:%M')

        pendientes = pedidos_con_coords.copy()
        ruta_optimizada = []
        distancia_total = 0
        tiempo_total = 0
        orden = 1

        while pendientes:
            # Encontrar el pedido más cercano (prioridad: distancia mínima)
            min_distancia = float('inf')
            pedido_mas_cercano = None

            for pedido in pendientes:
                distancia = RutasService._calcular_distancia_haversine(
                    lat_actual, lon_actual,
                    pedido.latitud, pedido.longitud
                )
                # Siempre elegir el más cercano, independiente de la hora de entrega
                if distancia < min_distancia:
                    min_distancia = distancia
                    pedido_mas_cercano = pedido

            if pedido_mas_cercano:
                # Agregar a la ruta
                distancia_total += min_distancia
                tiempo_estimado = int((min_distancia / 40) * 60)  # Asumiendo 40 km/h promedio en auto urbano
                tiempo_total += tiempo_estimado

                # Calcular hora estimada de llegada
                hora_llegada_estimada = hora_inicio_dt + timedelta(minutes=tiempo_total + (TIEMPO_ENTREGA_PROMEDIO * (orden - 1)))

                # Verificar si llegará tarde (solo como advertencia, no afecta la ruta)
                llegara_tarde = False
                if pedido_mas_cercano.fecha_entrega:
                    hora_solicitada = pedido_mas_cercano.fecha_entrega.time()
                    hora_estimada = hora_llegada_estimada.time()
                    llegara_tarde = hora_estimada > hora_solicitada

                ruta_optimizada.append({
                    'pedido_id': pedido_mas_cercano.id,
                    'orden': orden,
                    'distancia_desde_anterior_km': round(min_distancia, 2),
                    'tiempo_desde_anterior_min': tiempo_estimado,
                    'distancia_acumulada_km': round(distancia_total, 2),
                    'hora_llegada_estimada': hora_llegada_estimada.strftime('%H:%M'),
                    'llegara_tarde': llegara_tarde,  # Advertencia si llegará tarde
                    'latitud': pedido_mas_cercano.latitud,
                    'longitud': pedido_mas_cercano.longitud,
                    'direccion': pedido_mas_cercano.direccion_entrega,
                    'comuna': pedido_mas_cercano.comuna,
                    'cliente': pedido_mas_cercano.cliente_nombre,
                    'telefono': pedido_mas_cercano.cliente_telefono,
                    'hora_entrega': pedido_mas_cercano.fecha_entrega.strftime('%H:%M') if pedido_mas_cercano.fecha_entrega else None,
                    'es_urgente': pedido_mas_cercano.es_urgente
                })

                # Actualizar posición actual
                lat_actual = pedido_mas_cercano.latitud
                lon_actual = pedido_mas_cercano.longitud

                # Remover de pendientes
                pendientes.remove(pedido_mas_cercano)
                orden += 1

        return ruta_optimizada

    @staticmethod
    def optimizar_ruta_google(pedidos: List[Pedido], hora_inicio: str = HORA_INICIO_DEFAULT) -> Tuple[bool, Optional[Dict], str]:
        """
        Optimiza ruta usando Google Maps Directions API con waypoint optimization

        Args:
            pedidos: Lista de pedidos a incluir en la ruta
            hora_inicio: Hora de inicio de la ruta (formato HH:MM)

        Returns:
            (success, data, message)
        """
        try:
            api_key = RutasService._get_google_api_key()

            if not api_key:
                # Fallback a optimización simple
                ruta_simple = RutasService.optimizar_ruta_simple(pedidos, hora_inicio)

                # Generar link de Google Maps para navegación
                origen = f"{PUNTO_INICIO['latitud']},{PUNTO_INICIO['longitud']}"
                waypoints_coords = [f"{p['latitud']},{p['longitud']}" for p in ruta_simple]
                google_maps_url = f"https://www.google.com/maps/dir/{origen}/" + "/".join(waypoints_coords)

                return True, {
                    'ruta_optimizada': ruta_simple,
                    'metodo': 'simple',
                    'distancia_total_km': ruta_simple[-1]['distancia_acumulada_km'] if ruta_simple else 0,
                    'punto_inicio': PUNTO_INICIO,
                    'hora_inicio': hora_inicio,
                    'google_maps_url': google_maps_url
                }, 'Ruta optimizada con algoritmo simple (sin Google Maps)'

            # Filtrar pedidos con coordenadas
            # IMPORTANTE: Incluir TODOS los pedidos, incluso retiro_en_tienda (pueden tener coordenadas)
            pedidos_con_coords = [p for p in pedidos if p.latitud and p.longitud]
            pedidos_sin_coords = [p for p in pedidos if not (p.latitud and p.longitud)]

            # Intentar geocodificar pedidos sin coordenadas
            if pedidos_sin_coords:
                for pedido in pedidos_sin_coords:
                    if pedido.direccion_entrega:
                        coords = RutasService._geocodificar_direccion(
                            pedido.direccion_entrega,
                            pedido.comuna
                        )
                        if coords:
                            pedido.latitud = coords[0]
                            pedido.longitud = coords[1]
                            # Guardar coordenadas en la base de datos
                            try:
                                from extensions import db
                                db.session.add(pedido)
                                db.session.commit()
                            except Exception as e:
                                db.session.rollback()

                # Re-filtrar después de geocodificación
                pedidos_con_coords = [p for p in pedidos if p.latitud and p.longitud]
                pedidos_sin_coords = [p for p in pedidos if not (p.latitud and p.longitud)]

            if len(pedidos_con_coords) == 0:
                # Si ningún pedido tiene coordenadas, usar optimización simple que incluye todos
                ruta_simple = RutasService.optimizar_ruta_simple(pedidos, hora_inicio)
                
                # Generar link de Google Maps para navegación (solo con los que tienen dirección)
                origen = f"{PUNTO_INICIO['latitud']},{PUNTO_INICIO['longitud']}"
                waypoints_coords = []
                for p in ruta_simple:
                    if p.get('latitud') and p.get('longitud'):
                        waypoints_coords.append(f"{p['latitud']},{p['longitud']}")
                
                google_maps_url = f"https://www.google.com/maps/dir/{origen}"
                if waypoints_coords:
                    google_maps_url += "/" + "/".join(waypoints_coords)

                return True, {
                    'ruta_optimizada': ruta_simple,
                    'metodo': 'simple',
                    'distancia_total_km': ruta_simple[-1].get('distancia_acumulada_km', 0) if ruta_simple else 0,
                    'punto_inicio': PUNTO_INICIO,
                    'hora_inicio': hora_inicio,
                    'google_maps_url': google_maps_url,
                    'advertencia': f'{len(pedidos_sin_coords)} pedido(s) sin coordenadas incluidos en orden de entrega'
                }, f'Ruta optimizada (sin coordenadas GPS, usando orden de entrega). {len(pedidos_sin_coords)} pedido(s) sin coordenadas.'

            if len(pedidos_con_coords) == 1:
                # Solo un pedido, no es necesario optimizar
                pedido = pedidos_con_coords[0]

                # Generar link de Google Maps para navegación
                origen = f"{PUNTO_INICIO['latitud']},{PUNTO_INICIO['longitud']}"
                destino = f"{pedido.latitud},{pedido.longitud}"
                google_maps_url = f"https://www.google.com/maps/dir/{origen}/{destino}"

                return True, {
                    'ruta_optimizada': [{
                        'pedido_id': pedido.id,
                        'orden': 1,
                        'direccion': pedido.direccion_entrega,
                        'comuna': pedido.comuna,
                        'cliente': pedido.cliente_nombre,
                        'latitud': pedido.latitud,
                        'longitud': pedido.longitud
                    }],
                    'metodo': 'unico',
                    'punto_inicio': PUNTO_INICIO,
                    'google_maps_url': google_maps_url
                }, 'Ruta con un solo pedido'

            # Construir URL para Directions API
            origen = f"{PUNTO_INICIO['latitud']},{PUNTO_INICIO['longitud']}"

            # Google permite máximo 25 waypoints
            if len(pedidos_con_coords) > 25:
                pedidos_con_coords = pedidos_con_coords[:25]

            # IMPORTANTE: Para optimizar TODOS los pedidos, debemos incluirlos todos como waypoints
            # y usar el punto de inicio como destino (volver a la tienda después de todas las entregas)
            # Esto permite que Google optimice el orden de TODOS los pedidos

            waypoints = []
            for pedido in pedidos_con_coords:
                waypoints.append(f"{pedido.latitud},{pedido.longitud}")

            # Destino: volver al punto de inicio (tienda) después de todas las entregas
            # Esto permite que Google optimice el orden de TODOS los pedidos
            destino = f"{PUNTO_INICIO['latitud']},{PUNTO_INICIO['longitud']}"

            # Construir URL
            base_url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                'origin': origen,
                'destination': destino,
                'waypoints': 'optimize:true|' + '|'.join(waypoints),
                'mode': 'driving',  # Modo auto para entregas
                'key': api_key,
                'language': 'es',
                'region': 'CL'
            }

            # Hacer request
            response = requests.get(base_url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data['status'] != 'OK':
                error_msg = data.get('error_message', data['status'])
                # Fallback a optimización simple
                ruta_simple = RutasService.optimizar_ruta_simple(pedidos, hora_inicio)

                # Generar link de Google Maps para navegación
                origen = f"{PUNTO_INICIO['latitud']},{PUNTO_INICIO['longitud']}"
                waypoints_coords = [f"{p['latitud']},{p['longitud']}" for p in ruta_simple]
                google_maps_url = f"https://www.google.com/maps/dir/{origen}/" + "/".join(waypoints_coords)

                return True, {
                    'ruta_optimizada': ruta_simple,
                    'metodo': 'simple_fallback',
                    'distancia_total_km': ruta_simple[-1]['distancia_acumulada_km'] if ruta_simple else 0,
                    'punto_inicio': PUNTO_INICIO,
                    'hora_inicio': hora_inicio,
                    'google_maps_url': google_maps_url
                }, f'Usando optimización simple (Google API error: {error_msg})'

            # Procesar respuesta
            route = data['routes'][0]
            waypoint_order = route.get('waypoint_order', [])
            legs = route['legs']

            # Reconstruir orden optimizado de pedidos
            ruta_optimizada = []
            orden_pedidos = []

            # Agregar waypoints según orden optimizado de Google
            # waypoint_order contiene los índices de los waypoints en orden optimizado
            for idx in waypoint_order:
                if idx < len(pedidos_con_coords):
                    orden_pedidos.append(pedidos_con_coords[idx])

            # Verificar que todos los pedidos estén incluidos
            if len(orden_pedidos) != len(pedidos_con_coords):
                # Agregar los pedidos faltantes al final
                pedidos_faltantes = [p for p in pedidos_con_coords if p not in orden_pedidos]
                for pedido in pedidos_faltantes:
                    orden_pedidos.append(pedido)

            # Construir respuesta detallada
            distancia_acumulada = 0
            tiempo_acumulado = 0

            # Parsear hora de inicio
            hora_inicio_dt = datetime.strptime(hora_inicio, '%H:%M')

            # Los legs de Google Maps incluyen:
            # - legs[0]: origen -> primer waypoint optimizado
            # - legs[1]: primer waypoint -> segundo waypoint
            # - ...
            # - legs[N-1]: penúltimo waypoint -> último waypoint
            # - legs[N]: último waypoint -> destino (punto de inicio, vuelta a tienda)
            # 
            # Si tenemos N pedidos como waypoints, tendremos N+1 legs (incluye el de vuelta a la tienda)
            # Solo procesamos los primeros N legs (los que van a pedidos)
            
            if len(legs) == len(orden_pedidos) + 1:
                # Hay un leg extra para volver a la tienda, lo excluimos
                legs_para_pedidos = legs[:-1]
            else:
                # No hay leg de vuelta (caso especial), usar todos los legs
                legs_para_pedidos = legs[:len(orden_pedidos)]

            for idx, (pedido, leg) in enumerate(zip(orden_pedidos, legs_para_pedidos)):
                distancia_km = leg['distance']['value'] / 1000  # Convertir a km
                tiempo_min = leg['duration']['value'] / 60  # Convertir a minutos

                distancia_acumulada += distancia_km
                tiempo_acumulado += tiempo_min

                # Calcular hora estimada de llegada (hora inicio + tiempo acumulado + tiempo de entrega)
                hora_llegada_estimada = hora_inicio_dt + timedelta(minutes=int(tiempo_acumulado) + (TIEMPO_ENTREGA_PROMEDIO * idx))

                # Verificar si llegará tarde (solo como advertencia)
                llegara_tarde = False
                if pedido.fecha_entrega:
                    hora_solicitada = pedido.fecha_entrega.time()
                    hora_estimada = hora_llegada_estimada.time()
                    llegara_tarde = hora_estimada > hora_solicitada

                ruta_optimizada.append({
                    'pedido_id': pedido.id,
                    'orden': idx + 1,
                    'distancia_desde_anterior_km': round(distancia_km, 2),
                    'tiempo_desde_anterior_min': int(tiempo_min),
                    'distancia_acumulada_km': round(distancia_acumulada, 2),
                    'tiempo_acumulado_min': int(tiempo_acumulado),
                    'hora_llegada_estimada': hora_llegada_estimada.strftime('%H:%M'),
                    'llegara_tarde': llegara_tarde,  # Advertencia si llegará tarde
                    'latitud': pedido.latitud,
                    'longitud': pedido.longitud,
                    'direccion': pedido.direccion_entrega,
                    'comuna': pedido.comuna,
                    'cliente': pedido.cliente_nombre,
                    'telefono': pedido.cliente_telefono,
                    'hora_entrega': pedido.fecha_entrega.strftime('%H:%M') if pedido.fecha_entrega else None,
                    'es_urgente': pedido.es_urgente
                })

            # Si aún hay pedidos sin coordenadas, intentar insertarlos en la posición más cercana de la ruta
            # ANTES de generar el URL de Google Maps
            # basándose en la comuna o en la hora de entrega
            if pedidos_sin_coords:
                # Agrupar pedidos sin coordenadas por comuna
                pedidos_por_comuna = {}
                for pedido in pedidos_sin_coords:
                    comuna = pedido.comuna or 'Sin Comuna'
                    if comuna not in pedidos_por_comuna:
                        pedidos_por_comuna[comuna] = []
                    pedidos_por_comuna[comuna].append(pedido)
                
                # Para cada pedido sin coordenadas, encontrar la mejor posición en la ruta
                for comuna, pedidos_comuna in pedidos_por_comuna.items():
                    for pedido in sorted(pedidos_comuna, key=lambda x: x.fecha_entrega if x.fecha_entrega else datetime.max):
                        mejor_posicion = len(ruta_optimizada)  # Por defecto al final
                        mejor_distancia = float('inf')
                        
                        # Buscar pedidos en la misma comuna en la ruta
                        for idx, parada in enumerate(ruta_optimizada):
                            if parada.get('comuna') == comuna:
                                # Insertar después de este pedido
                                mejor_posicion = idx + 1
                                break
                        
                        # Si no hay pedidos en la misma comuna, buscar el más cercano por hora de entrega
                        if mejor_posicion == len(ruta_optimizada):
                            if pedido.fecha_entrega:
                                hora_pedido = pedido.fecha_entrega.time()
                                for idx, parada in enumerate(ruta_optimizada):
                                    if parada.get('hora_entrega'):
                                        try:
                                            hora_parada = datetime.strptime(parada['hora_entrega'], '%H:%M').time()
                                            if hora_parada <= hora_pedido:
                                                mejor_posicion = idx + 1
                                        except:
                                            pass
                        
                        # Insertar en la mejor posición
                        nueva_parada = {
                            'pedido_id': pedido.id,
                            'orden': mejor_posicion + 1,  # Se ajustará después
                            'distancia_desde_anterior_km': None,
                            'tiempo_desde_anterior_min': None,
                            'distancia_acumulada_km': ruta_optimizada[mejor_posicion - 1]['distancia_acumulada_km'] if mejor_posicion > 0 else 0,
                            'tiempo_acumulado_min': ruta_optimizada[mejor_posicion - 1]['tiempo_acumulado_min'] if mejor_posicion > 0 else 0,
                            'hora_llegada_estimada': None,
                            'llegara_tarde': False,
                            'latitud': None,
                            'longitud': None,
                            'direccion': pedido.direccion_entrega,
                            'comuna': pedido.comuna,
                            'cliente': pedido.cliente_nombre,
                            'telefono': pedido.cliente_telefono,
                            'hora_entrega': pedido.fecha_entrega.strftime('%H:%M') if pedido.fecha_entrega else None,
                            'es_urgente': pedido.es_urgente,
                            'sin_coordenadas': True
                        }
                        
                        ruta_optimizada.insert(mejor_posicion, nueva_parada)
                
                # Re-numerar órdenes después de las inserciones
                for idx, parada in enumerate(ruta_optimizada):
                    parada['orden'] = idx + 1

            # Generar link de Google Maps para navegación (solo con pedidos que tienen coordenadas)
            # Formato: https://www.google.com/maps/dir/origin/waypoint1/waypoint2/.../destination
            waypoints_coords = [f"{p['latitud']},{p['longitud']}" for p in ruta_optimizada if p.get('latitud') and p.get('longitud')]
            google_maps_url = f"https://www.google.com/maps/dir/{origen}/" + "/".join(waypoints_coords)

            # La distancia total es solo hasta el último pedido (sin incluir vuelta a tienda)
            distancia_total_km = round(distancia_acumulada, 2)
            tiempo_total_min = int(tiempo_acumulado)

            mensaje_final = 'Ruta optimizada con Google Maps Directions API'
            if pedidos_sin_coords:
                mensaje_final += f'. {len(pedidos_sin_coords)} pedido(s) sin coordenadas insertado(s) en la ruta.'

            return True, {
                'ruta_optimizada': ruta_optimizada,
                'metodo': 'google_directions',
                'distancia_total_km': distancia_total_km,
                'tiempo_total_min': tiempo_total_min,
                'punto_inicio': PUNTO_INICIO,
                'hora_inicio': hora_inicio,
                'polyline': route.get('overview_polyline', {}).get('points'),  # Para dibujar ruta en mapa
                'google_maps_url': google_maps_url,  # Link para abrir en Google Maps
                'pedidos_sin_coordenadas': len(pedidos_sin_coords)  # Información adicional
            }, mensaje_final

        except requests.exceptions.RequestException as e:
            # Fallback a optimización simple
            ruta_simple = RutasService.optimizar_ruta_simple(pedidos, hora_inicio)

            # Generar link de Google Maps para navegación
            origen = f"{PUNTO_INICIO['latitud']},{PUNTO_INICIO['longitud']}"
            waypoints_coords = [f"{p['latitud']},{p['longitud']}" for p in ruta_simple]
            google_maps_url = f"https://www.google.com/maps/dir/{origen}/" + "/".join(waypoints_coords)

            return True, {
                'ruta_optimizada': ruta_simple,
                'metodo': 'simple_fallback',
                'distancia_total_km': ruta_simple[-1]['distancia_acumulada_km'] if ruta_simple else 0,
                'punto_inicio': PUNTO_INICIO,
                'hora_inicio': hora_inicio,
                'google_maps_url': google_maps_url
            }, 'Usando optimización simple (error de conexión con Google)'

        except Exception as e:
            return False, None, f'Error al optimizar ruta: {str(e)}'

    @staticmethod
    def calcular_hora_estimada_llegada(hora_inicio: str, tiempo_hasta_entrega_min: int) -> str:
        """
        Calcula hora estimada de llegada basada en hora de inicio y tiempo de viaje

        Args:
            hora_inicio: Hora de inicio (HH:MM)
            tiempo_hasta_entrega_min: Minutos desde el inicio hasta esta entrega

        Returns:
            Hora estimada (HH:MM)
        """
        try:
            hora, minuto = map(int, hora_inicio.split(':'))
            inicio = datetime.now().replace(hour=hora, minute=minuto, second=0, microsecond=0)
            llegada = inicio + timedelta(minutes=tiempo_hasta_entrega_min)
            return llegada.strftime('%H:%M')
        except:
            return '??:??'
