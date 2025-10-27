"""
Rutas para análisis de pedidos y personalizaciones
"""

from flask import Blueprint, jsonify, request
from extensions import db
from models.pedido import Pedido, PedidoInsumo
from models.producto import Producto
from models.inventario import Flor, Contenedor
from sqlalchemy import func, desc
import json

bp = Blueprint('analisis', __name__, url_prefix='/api/analisis')

@bp.route('/personalizaciones', methods=['GET'])
def analisis_personalizaciones():
    """
    Obtiene análisis detallado de pedidos personalizados
    """
    try:
        # Obtener productos marcados como personalización
        productos_personalizacion = Producto.query.filter_by(es_personalizacion=True).all()
        ids_personalizacion = [p.id for p in productos_personalizacion]
        
        if not ids_personalizacion:
            return jsonify({
                'success': True,
                'mensaje': 'No hay productos de personalización configurados',
                'data': {
                    'total_pedidos': 0,
                    'ingresos_totales': 0,
                    'pedidos': [],
                    'estadisticas': {}
                }
            })
        
        # Obtener todos los pedidos personalizados
        pedidos_personalizados = Pedido.query.filter(
            Pedido.producto_id.in_(ids_personalizacion)
        ).all()
        
        # Calcular estadísticas
        total_pedidos = len(pedidos_personalizados)
        ingresos_totales = sum([float(p.precio_total) for p in pedidos_personalizados])
        
        # Análisis por tipo de personalización
        tipos_personalizacion = db.session.query(
            Pedido.tipo_personalizacion,
            func.count(Pedido.id).label('cantidad'),
            func.sum(Pedido.precio_ramo + Pedido.precio_envio).label('ingresos')
        ).filter(
            Pedido.producto_id.in_(ids_personalizacion)
        ).group_by(
            Pedido.tipo_personalizacion
        ).all()
        
        # Análisis de insumos más usados en personalizaciones
        insumos_flores = db.session.query(
            PedidoInsumo.insumo_id,
            func.sum(PedidoInsumo.cantidad).label('cantidad_total'),
            func.count(PedidoInsumo.pedido_id).label('veces_usado')
        ).join(
            Pedido, Pedido.id == PedidoInsumo.pedido_id
        ).filter(
            Pedido.producto_id.in_(ids_personalizacion),
            PedidoInsumo.insumo_tipo == 'Flor'
        ).group_by(
            PedidoInsumo.insumo_id
        ).order_by(
            desc('cantidad_total')
        ).limit(10).all()
        
        # Obtener nombres de flores
        flores_mas_usadas = []
        for insumo in insumos_flores:
            flor = Flor.query.get(insumo.insumo_id)
            if flor:
                flores_mas_usadas.append({
                    'id': insumo.insumo_id,
                    'nombre': flor.nombre or f"{flor.tipo} {flor.color}",
                    'cantidad_total': insumo.cantidad_total,
                    'veces_usado': insumo.veces_usado
                })
        
        # Análisis de contenedores
        insumos_contenedores = db.session.query(
            PedidoInsumo.insumo_id,
            func.count(PedidoInsumo.pedido_id).label('veces_usado')
        ).join(
            Pedido, Pedido.id == PedidoInsumo.pedido_id
        ).filter(
            Pedido.producto_id.in_(ids_personalizacion),
            PedidoInsumo.insumo_tipo == 'Contenedor'
        ).group_by(
            PedidoInsumo.insumo_id
        ).order_by(
            desc('veces_usado')
        ).limit(10).all()
        
        # Obtener nombres de contenedores
        contenedores_mas_usados = []
        for insumo in insumos_contenedores:
            contenedor = Contenedor.query.get(insumo.insumo_id)
            if contenedor:
                contenedores_mas_usados.append({
                    'id': insumo.insumo_id,
                    'nombre': contenedor.nombre or contenedor.tipo,
                    'veces_usado': insumo.veces_usado
                })
        
        # Análisis de colores solicitados
        colores_count = {}
        for pedido in pedidos_personalizados:
            if pedido.colores_solicitados:
                try:
                    colores = json.loads(pedido.colores_solicitados)
                    for color in colores:
                        colores_count[color] = colores_count.get(color, 0) + 1
                except:
                    pass
        
        colores_populares = sorted(
            [{'color': k, 'cantidad': v} for k, v in colores_count.items()],
            key=lambda x: x['cantidad'],
            reverse=True
        )[:10]
        
        # Motivos más comunes
        motivos = db.session.query(
            Pedido.motivo,
            func.count(Pedido.id).label('cantidad')
        ).filter(
            Pedido.producto_id.in_(ids_personalizacion),
            Pedido.motivo.isnot(None)
        ).group_by(
            Pedido.motivo
        ).order_by(
            desc('cantidad')
        ).limit(10).all()
        
        # Análisis temporal (por mes)
        pedidos_por_mes = db.session.query(
            func.strftime('%Y-%m', Pedido.fecha_pedido).label('mes'),
            func.count(Pedido.id).label('cantidad'),
            func.sum(Pedido.precio_ramo + Pedido.precio_envio).label('ingresos')
        ).filter(
            Pedido.producto_id.in_(ids_personalizacion)
        ).group_by(
            'mes'
        ).order_by(
            'mes'
        ).all()
        
        return jsonify({
            'success': True,
            'data': {
                'resumen': {
                    'total_pedidos': total_pedidos,
                    'ingresos_totales': float(ingresos_totales),
                    'ticket_promedio': float(ingresos_totales / total_pedidos) if total_pedidos > 0 else 0
                },
                'por_tipo': [
                    {
                        'tipo': t.tipo_personalizacion or 'Sin especificar',
                        'cantidad': t.cantidad,
                        'ingresos': float(t.ingresos or 0)
                    }
                    for t in tipos_personalizacion
                ],
                'flores_mas_usadas': flores_mas_usadas,
                'contenedores_mas_usados': contenedores_mas_usados,
                'colores_populares': colores_populares,
                'motivos_comunes': [
                    {'motivo': m.motivo, 'cantidad': m.cantidad}
                    for m in motivos
                ],
                'tendencia_temporal': [
                    {
                        'mes': pm.mes,
                        'cantidad': pm.cantidad,
                        'ingresos': float(pm.ingresos or 0)
                    }
                    for pm in pedidos_por_mes
                ]
            }
        })
        
    except Exception as e:
        print(f"Error en análisis de personalizaciones: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@bp.route('/personalizaciones/detalle', methods=['GET'])
def detalle_personalizaciones():
    """
    Obtiene listado detallado de todos los pedidos personalizados
    """
    try:
        # Parámetros de paginación
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        
        # Obtener productos marcados como personalización
        productos_personalizacion = Producto.query.filter_by(es_personalizacion=True).all()
        ids_personalizacion = [p.id for p in productos_personalizacion]
        
        if not ids_personalizacion:
            return jsonify({
                'success': True,
                'data': [],
                'total': 0,
                'page': page,
                'total_pages': 0
            })
        
        # Query con paginación
        query = Pedido.query.filter(
            Pedido.producto_id.in_(ids_personalizacion)
        ).order_by(desc(Pedido.fecha_pedido))
        
        total = query.count()
        pedidos = query.paginate(page=page, per_page=limit, error_out=False)
        
        # Obtener insumos de cada pedido
        pedidos_detalle = []
        for pedido in pedidos.items:
            insumos = PedidoInsumo.query.filter_by(pedido_id=pedido.id).all()
            
            insumos_detalle = []
            for insumo in insumos:
                if insumo.insumo_tipo == 'Flor':
                    flor = Flor.query.get(insumo.insumo_id)
                    nombre = flor.nombre or f"{flor.tipo} {flor.color}" if flor else 'Desconocida'
                else:
                    contenedor = Contenedor.query.get(insumo.insumo_id)
                    nombre = contenedor.nombre or contenedor.tipo if contenedor else 'Desconocido'
                
                insumos_detalle.append({
                    'tipo': insumo.insumo_tipo,
                    'nombre': nombre,
                    'cantidad': insumo.cantidad,
                    'costo_total': float(insumo.costo_total)
                })
            
            pedidos_detalle.append({
                **pedido.to_dict(),
                'insumos': insumos_detalle
            })
        
        return jsonify({
            'success': True,
            'data': pedidos_detalle,
            'total': total,
            'page': page,
            'total_pages': pedidos.pages
        })
        
    except Exception as e:
        print(f"Error en detalle de personalizaciones: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

