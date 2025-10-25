"""
Rutas para optimización de despachos y rutas
"""

from flask import Blueprint, request, jsonify
from extensions import db
from models.pedido import Pedido
from config.comunas import obtener_precio_comuna, obtener_zona_comuna, ZONAS, COMUNAS_PRECIOS
from datetime import datetime, timedelta
from sqlalchemy import func, extract

bp = Blueprint('rutas', __name__)

@bp.route('/optimizar', methods=['GET'])
def optimizar_rutas():
    """
    Obtener pedidos agrupados por comuna para optimizar rutas de despacho
    """
    try:
        # Parámetros de filtro
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        solo_pendientes = request.args.get('solo_pendientes', 'true').lower() == 'true'
        
        # Query base
        query = Pedido.query
        
        # Filtrar solo pedidos activos (no archivados ni cancelados)
        if solo_pendientes:
            query = query.filter(
                Pedido.estado.in_(['Pedido', 'Pedidos Semana', 'Entregas para Mañana', 
                                   'Entregas de Hoy', 'En Proceso', 'Listo para Despacho'])
            )
        
        # Filtrar por rango de fechas
        if fecha_desde:
            query = query.filter(Pedido.fecha_entrega >= datetime.fromisoformat(fecha_desde))
        if fecha_hasta:
            query = query.filter(Pedido.fecha_entrega <= datetime.fromisoformat(fecha_hasta))
        
        # Obtener todos los pedidos
        pedidos = query.order_by(Pedido.fecha_entrega.asc()).all()
        
        # Agrupar por comuna
        por_comuna = {}
        for pedido in pedidos:
            # Obtener comuna del pedido (o extraer de la dirección si no existe)
            comuna = pedido.comuna or extraer_comuna(pedido.direccion_entrega or '')
            
            if comuna not in por_comuna:
                por_comuna[comuna] = {
                    'comuna': comuna,
                    'precio_envio': obtener_precio_comuna(comuna),
                    'zona': obtener_zona_comuna(comuna),
                    'pedidos': [],
                    'total_pedidos': 0,
                    'total_envios': 0
                }
            
            por_comuna[comuna]['pedidos'].append(pedido.to_dict())
            por_comuna[comuna]['total_pedidos'] += 1
            por_comuna[comuna]['total_envios'] += float(pedido.precio_envio or 0)
        
        # Convertir a lista y ordenar por zona y precio
        rutas_optimizadas = list(por_comuna.values())
        rutas_optimizadas.sort(key=lambda x: (x['precio_envio'], x['comuna']))
        
        return jsonify({
            'success': True,
            'data': rutas_optimizadas,
            'total_comunas': len(rutas_optimizadas),
            'total_pedidos': sum(r['total_pedidos'] for r in rutas_optimizadas)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/por-fecha', methods=['GET'])
def rutas_por_fecha():
    """
    Obtener pedidos agrupados por fecha y comuna
    """
    try:
        # Parámetros
        dias_adelante = request.args.get('dias', 7, type=int)
        
        # Calcular rango de fechas
        hoy = datetime.now().date()
        fecha_limite = hoy + timedelta(days=dias_adelante)
        
        # Query
        pedidos = Pedido.query.filter(
            Pedido.fecha_entrega >= hoy,
            Pedido.fecha_entrega <= fecha_limite,
            Pedido.estado.in_(['Pedido', 'Pedidos Semana', 'Entregas para Mañana', 
                               'Entregas de Hoy', 'En Proceso', 'Listo para Despacho'])
        ).order_by(Pedido.fecha_entrega.asc()).all()
        
        # Agrupar por fecha y luego por comuna
        por_fecha = {}
        for pedido in pedidos:
            fecha_str = pedido.fecha_entrega.strftime('%Y-%m-%d') if pedido.fecha_entrega else 'Sin fecha'
            
            if fecha_str not in por_fecha:
                por_fecha[fecha_str] = {
                    'fecha': fecha_str,
                    'comunas': {},
                    'total_pedidos': 0
                }
            
            # Obtener comuna del pedido (o extraer de la dirección si no existe)
            comuna = pedido.comuna or extraer_comuna(pedido.direccion_entrega or '')
            
            if comuna not in por_fecha[fecha_str]['comunas']:
                por_fecha[fecha_str]['comunas'][comuna] = {
                    'comuna': comuna,
                    'precio_envio': obtener_precio_comuna(comuna),
                    'pedidos': []
                }
            
            por_fecha[fecha_str]['comunas'][comuna]['pedidos'].append(pedido.to_dict())
            por_fecha[fecha_str]['total_pedidos'] += 1
        
        # Convertir a lista
        resultado = []
        for fecha, data in sorted(por_fecha.items()):
            comunas_lista = list(data['comunas'].values())
            comunas_lista.sort(key=lambda x: (x['precio_envio'], x['comuna']))
            
            resultado.append({
                'fecha': fecha,
                'total_pedidos': data['total_pedidos'],
                'comunas': comunas_lista
            })
        
        return jsonify({
            'success': True,
            'data': resultado,
            'total_dias': len(resultado)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/comunas', methods=['GET'])
def listar_comunas():
    """Listar todas las comunas con sus precios"""
    try:
        comunas = []
        for comuna, precio in sorted(COMUNAS_PRECIOS.items(), key=lambda x: (x[1], x[0])):
            comunas.append({
                'comuna': comuna,
                'precio': precio,
                'zona': obtener_zona_comuna(comuna)
            })
        
        return jsonify({
            'success': True,
            'data': comunas,
            'zonas': ZONAS
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def extraer_comuna(direccion):
    """
    Extrae el nombre de la comuna de una dirección
    Intenta identificar la comuna en el texto de la dirección
    """
    direccion_lower = direccion.lower()
    
    # Buscar coincidencias con comunas conocidas
    for comuna in COMUNAS_PRECIOS.keys():
        if comuna.lower() in direccion_lower:
            return comuna
    
    # Si no se encuentra, intentar extraer la última parte de la dirección
    # que típicamente es la comuna
    partes = direccion.split(',')
    if len(partes) >= 2:
        posible_comuna = partes[-1].strip()
        
        # Buscar coincidencia parcial
        for comuna in COMUNAS_PRECIOS.keys():
            if posible_comuna.lower() in comuna.lower() or comuna.lower() in posible_comuna.lower():
                return comuna
        
        return posible_comuna
    
    return 'Sin especificar'


@bp.route('/resumen-hoy', methods=['GET'])
def resumen_hoy():
    """Resumen de entregas para hoy"""
    try:
        hoy = datetime.now().date()
        
        pedidos_hoy = Pedido.query.filter(
            func.date(Pedido.fecha_entrega) == hoy,
            Pedido.estado.in_(['Entregas de Hoy', 'En Proceso', 'Listo para Despacho'])
        ).all()
        
        # Agrupar por comuna
        por_comuna = {}
        for pedido in pedidos_hoy:
            comuna = pedido.comuna or extraer_comuna(pedido.direccion_entrega or '')
            
            if comuna not in por_comuna:
                por_comuna[comuna] = []
            
            por_comuna[comuna].append(pedido.to_dict())
        
        # Formatear resultado
        resultado = []
        for comuna, pedidos in sorted(por_comuna.items()):
            resultado.append({
                'comuna': comuna,
                'precio_envio': obtener_precio_comuna(comuna),
                'cantidad': len(pedidos),
                'pedidos': pedidos
            })
        
        resultado.sort(key=lambda x: (x['precio_envio'], x['comuna']))
        
        return jsonify({
            'success': True,
            'fecha': hoy.isoformat(),
            'total_pedidos': len(pedidos_hoy),
            'data': resultado
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

