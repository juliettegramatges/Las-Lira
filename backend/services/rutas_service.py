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
    def optimizar_ruta_simple(pedidos: List[Pedido]) -> List[Dict]:
        """
        Optimiza ruta usando algoritmo greedy (vecino más cercano)
        No requiere API de Google, usa coordenadas GPS directamente
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

        pendientes = pedidos_con_coords.copy()
        ruta_optimizada = []
        distancia_total = 0
        orden = 1

        while pendientes:
            # Encontrar el pedido más cercano
            min_distancia = float('inf')
            pedido_mas_cercano = None

            for pedido in pendientes:
                distancia = RutasService._calcular_distancia_haversine(
                    lat_actual, lon_actual,
                    pedido.latitud, pedido.longitud
                )
                if distancia < min_distancia:
                    min_distancia = distancia
                    pedido_mas_cercano = pedido

            if pedido_mas_cercano:
                # Agregar a la ruta
                distancia_total += min_distancia
                tiempo_estimado = int((min_distancia / 40) * 60)  # Asumiendo 40 km/h promedio en auto urbano

                ruta_optimizada.append({
                    'pedido_id': pedido_mas_cercano.id,
                    'orden': orden,
                    'distancia_desde_anterior_km': round(min_distancia, 2),
                    'tiempo_desde_anterior_min': tiempo_estimado,
                    'distancia_acumulada_km': round(distancia_total, 2),
                    'latitud': pedido_mas_cercano.latitud,
                    'longitud': pedido_mas_cercano.longitud,
                    'direccion': pedido_mas_cercano.direccion_entrega,
                    'comuna': pedido_mas_cercano.comuna,
                    'cliente': pedido_mas_cercano.cliente_nombre,
                    'telefono': pedido_mas_cercano.cliente_telefono,
                    'hora_entrega': pedido_mas_cercano.fecha_entrega.strftime('%H:%M') if pedido_mas_cercano.fecha_entrega else None
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
                print("⚠️  No se encontró API Key de Google, usando optimización simple")
                ruta_simple = RutasService.optimizar_ruta_simple(pedidos)

                # Generar link de Google Maps para navegación
                origen = f"{PUNTO_INICIO['latitud']},{PUNTO_INICIO['longitud']}"
                waypoints_coords = [f"{p['latitud']},{p['longitud']}" for p in ruta_simple]
                google_maps_url = f"https://www.google.com/maps/dir/{origen}/" + "/".join(waypoints_coords)

                return True, {
                    'ruta_optimizada': ruta_simple,
                    'metodo': 'simple',
                    'distancia_total_km': ruta_simple[-1]['distancia_acumulada_km'] if ruta_simple else 0,
                    'punto_inicio': PUNTO_INICIO,
                    'google_maps_url': google_maps_url
                }, 'Ruta optimizada con algoritmo simple (sin Google Maps)'

            # Filtrar pedidos con coordenadas
            pedidos_con_coords = [p for p in pedidos if p.latitud and p.longitud]

            if len(pedidos_con_coords) == 0:
                return False, None, 'No hay pedidos con coordenadas GPS'

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
                print(f"⚠️  Limitando a 25 pedidos (máximo de Google Maps API)")

            # Waypoints intermedios (todos los pedidos excepto el último)
            waypoints = []
            for pedido in pedidos_con_coords[:-1]:
                waypoints.append(f"{pedido.latitud},{pedido.longitud}")

            # Destino (último pedido)
            destino = f"{pedidos_con_coords[-1].latitud},{pedidos_con_coords[-1].longitud}"

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
                print(f"❌ Error de Google Maps API: {error_msg}")
                # Fallback a optimización simple
                ruta_simple = RutasService.optimizar_ruta_simple(pedidos)
                return True, {
                    'ruta_optimizada': ruta_simple,
                    'metodo': 'simple_fallback',
                    'distancia_total_km': ruta_simple[-1]['distancia_acumulada_km'] if ruta_simple else 0,
                    'punto_inicio': PUNTO_INICIO
                }, f'Usando optimización simple (Google API error: {error_msg})'

            # Procesar respuesta
            route = data['routes'][0]
            waypoint_order = route.get('waypoint_order', [])
            legs = route['legs']

            # Reconstruir orden optimizado de pedidos
            ruta_optimizada = []
            orden_pedidos = []

            # Agregar waypoints según orden optimizado
            for idx in waypoint_order:
                orden_pedidos.append(pedidos_con_coords[idx])

            # Agregar el último pedido (destino)
            orden_pedidos.append(pedidos_con_coords[-1])

            # Construir respuesta detallada
            distancia_acumulada = 0
            tiempo_acumulado = 0

            for idx, (pedido, leg) in enumerate(zip(orden_pedidos, legs)):
                distancia_km = leg['distance']['value'] / 1000  # Convertir a km
                tiempo_min = leg['duration']['value'] / 60  # Convertir a minutos

                distancia_acumulada += distancia_km
                tiempo_acumulado += tiempo_min

                ruta_optimizada.append({
                    'pedido_id': pedido.id,
                    'orden': idx + 1,
                    'distancia_desde_anterior_km': round(distancia_km, 2),
                    'tiempo_desde_anterior_min': int(tiempo_min),
                    'distancia_acumulada_km': round(distancia_acumulada, 2),
                    'tiempo_acumulado_min': int(tiempo_acumulado),
                    'latitud': pedido.latitud,
                    'longitud': pedido.longitud,
                    'direccion': pedido.direccion_entrega,
                    'comuna': pedido.comuna,
                    'cliente': pedido.cliente_nombre,
                    'telefono': pedido.cliente_telefono,
                    'hora_entrega': pedido.fecha_entrega.strftime('%H:%M') if pedido.fecha_entrega else None,
                    'es_urgente': pedido.es_urgente
                })

            # Generar link de Google Maps para navegación
            # Formato: https://www.google.com/maps/dir/origin/waypoint1/waypoint2/.../destination
            waypoints_coords = [f"{p['latitud']},{p['longitud']}" for p in ruta_optimizada]
            google_maps_url = f"https://www.google.com/maps/dir/{origen}/" + "/".join(waypoints_coords)

            return True, {
                'ruta_optimizada': ruta_optimizada,
                'metodo': 'google_directions',
                'distancia_total_km': round(distancia_acumulada, 2),
                'tiempo_total_min': int(tiempo_acumulado),
                'punto_inicio': PUNTO_INICIO,
                'hora_inicio': hora_inicio,
                'polyline': route.get('overview_polyline', {}).get('points'),  # Para dibujar ruta en mapa
                'google_maps_url': google_maps_url  # Link para abrir en Google Maps
            }, 'Ruta optimizada con Google Maps Directions API'

        except requests.exceptions.RequestException as e:
            print(f"❌ Error de red al consultar Google Maps: {e}")
            # Fallback a optimización simple
            ruta_simple = RutasService.optimizar_ruta_simple(pedidos)

            # Generar link de Google Maps para navegación
            origen = f"{PUNTO_INICIO['latitud']},{PUNTO_INICIO['longitud']}"
            waypoints_coords = [f"{p['latitud']},{p['longitud']}" for p in ruta_simple]
            google_maps_url = f"https://www.google.com/maps/dir/{origen}/" + "/".join(waypoints_coords)

            return True, {
                'ruta_optimizada': ruta_simple,
                'metodo': 'simple_fallback',
                'distancia_total_km': ruta_simple[-1]['distancia_acumulada_km'] if ruta_simple else 0,
                'punto_inicio': PUNTO_INICIO,
                'google_maps_url': google_maps_url
            }, 'Usando optimización simple (error de conexión con Google)'

        except Exception as e:
            print(f"❌ Error inesperado en optimización de ruta: {e}")
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
