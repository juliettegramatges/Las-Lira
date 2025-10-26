"""
Rutas para gestión de productos y catálogo
"""

from flask import Blueprint, request, jsonify
from extensions import db
from models.producto import Producto, RecetaProducto
from models.inventario import Flor, Contenedor

bp = Blueprint('productos', __name__)

@bp.route('/', methods=['GET'])
def listar_productos():
    """Listar productos con paginación y búsqueda"""
    try:
        disponible_shopify = request.args.get('disponible_shopify', type=bool)
        activo = request.args.get('activo', type=bool, default=True)
        busqueda = request.args.get('busqueda', '').strip()
        
        # Parámetros de paginación
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))
        
        query = Producto.query
        
        if disponible_shopify is not None:
            query = query.filter_by(disponible_shopify=disponible_shopify)
        if activo is not None:
            query = query.filter_by(activo=activo)
        
        # Aplicar búsqueda
        if busqueda:
            query = query.filter(
                db.or_(
                    Producto.nombre.ilike(f'%{busqueda}%'),
                    Producto.descripcion.ilike(f'%{busqueda}%'),
                    Producto.categoria.ilike(f'%{busqueda}%')
                )
            )
        
        # Contar total antes de paginar
        total = query.count()
        
        # Estadísticas globales (sin filtro de búsqueda)
        stats_query = Producto.query
        if activo is not None:
            stats_query = stats_query.filter_by(activo=activo)
        
        total_global = stats_query.count()
        con_foto = stats_query.filter(Producto.foto_url.isnot(None)).count()
        disponibles_shopify = stats_query.filter_by(disponible_shopify=True).count()
        
        # Aplicar paginación
        productos = query.order_by(Producto.nombre).limit(limit).offset((page - 1) * limit).all()
        
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in productos],
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit,
            'stats': {
                'total_global': total_global,
                'con_foto': con_foto,
                'disponibles_shopify': disponibles_shopify,
                'sin_foto': total_global - con_foto
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<producto_id>', methods=['GET'])
def obtener_producto(producto_id):
    """Obtener detalles de un producto con su receta"""
    try:
        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'data': producto.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<producto_id>/receta', methods=['GET'])
def obtener_receta_producto(producto_id):
    """Obtener receta detallada de un producto (insumos necesarios)"""
    try:
        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        # Obtener recetas con detalles de cada insumo
        recetas_detalladas = []
        costo_total_insumos = 0
        
        for receta in producto.recetas:
            detalle = {
                'id': receta.id,
                'tipo': receta.insumo_tipo,
                'tipo_insumo': receta.insumo_tipo,  # Compatibilidad con frontend
                'insumo_id': receta.insumo_id,
                'cantidad': receta.cantidad,
                'unidad': receta.unidad,
                'es_opcional': receta.es_opcional,
                'notas': receta.notas
            }
            
            # Obtener detalles del insumo
            if receta.insumo_tipo == 'Flor':
                flor = Flor.query.get(receta.insumo_id)
                if flor:
                    # Usar el nombre si existe, sino construirlo desde tipo y color
                    nombre_flor = flor.nombre or f"{flor.tipo or ''} {flor.color or ''}".strip() or 'Flor sin nombre'
                    detalle['nombre'] = nombre_flor
                    detalle['insumo_nombre'] = nombre_flor  # Compatibilidad con frontend
                    detalle['color'] = flor.color or ''
                    detalle['costo_unitario'] = float(flor.costo_unitario) if flor.costo_unitario else 0
                    detalle['stock_disponible'] = flor.cantidad_stock or 0
                    detalle['unidad_stock'] = flor.unidad or 'Tallos'
                    detalle['costo_total'] = float(flor.costo_unitario if flor.costo_unitario else 0) * receta.cantidad
                    detalle['foto_url'] = flor.foto_url
                    costo_total_insumos += detalle['costo_total']
                    detalle['disponible'] = (flor.cantidad_stock or 0) >= receta.cantidad
                else:
                    detalle['nombre'] = 'Flor no encontrada'
                    detalle['insumo_nombre'] = 'Flor no encontrada'
                    detalle['color'] = ''
                    detalle['disponible'] = False
                    detalle['costo_unitario'] = 0
                    detalle['costo_total'] = 0
                    detalle['stock_disponible'] = 0
                    
            else:  # Contenedor
                contenedor = Contenedor.query.get(receta.insumo_id)
                if contenedor:
                    # Usar el nombre si existe, sino el tipo
                    nombre_contenedor = contenedor.nombre or contenedor.tipo or 'Contenedor sin nombre'
                    detalle['nombre'] = nombre_contenedor
                    detalle['insumo_nombre'] = nombre_contenedor  # Compatibilidad con frontend
                    detalle['costo_unitario'] = float(contenedor.costo) if contenedor.costo else 0
                    detalle['stock_disponible'] = contenedor.cantidad_stock or 0
                    detalle['costo_total'] = float(contenedor.costo if contenedor.costo else 0) * receta.cantidad
                    detalle['foto_url'] = contenedor.foto_url if hasattr(contenedor, 'foto_url') else None
                    costo_total_insumos += detalle['costo_total']
                    detalle['disponible'] = (contenedor.cantidad_stock or 0) >= receta.cantidad
                else:
                    detalle['nombre'] = 'Contenedor no encontrado'
                    detalle['insumo_nombre'] = 'Contenedor no encontrado'
                    detalle['costo_unitario'] = 0
                    detalle['costo_total'] = 0
                    detalle['stock_disponible'] = 0
                    detalle['disponible'] = False
            
            recetas_detalladas.append(detalle)
        
        # Calcular margen
        precio_venta = float(producto.precio_venta) if producto.precio_venta else 0
        margen = ((precio_venta - costo_total_insumos) / precio_venta * 100) if precio_venta > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'producto': producto.to_dict(),
                'receta': recetas_detalladas,
                'costo_total_insumos': round(costo_total_insumos, 2),
                'precio_venta': precio_venta,
                'margen_porcentaje': round(margen, 2),
                'ganancia': round(precio_venta - costo_total_insumos, 2)
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<producto_id>/verificar-stock', methods=['GET'])
def verificar_stock_producto(producto_id):
    """Verificar si hay stock suficiente para preparar un producto"""
    try:
        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        faltantes = []
        disponible = True
        
        for receta in producto.recetas:
            if receta.insumo_tipo == 'Flor':
                flor = Flor.query.get(receta.insumo_id)
                if not flor or flor.cantidad_stock < receta.cantidad:
                    disponible = False
                    faltantes.append({
                        'tipo': 'Flor',
                        'id': receta.insumo_id,
                        'nombre': f"{flor.tipo} {flor.color}" if flor else "Desconocido",
                        'necesario': receta.cantidad,
                        'disponible': flor.cantidad_stock if flor else 0
                    })
            else:  # Contenedor
                contenedor = Contenedor.query.get(receta.insumo_id)
                if not contenedor or contenedor.stock < receta.cantidad:
                    disponible = False
                    faltantes.append({
                        'tipo': 'Contenedor',
                        'id': receta.insumo_id,
                        'nombre': f"{contenedor.tipo} {contenedor.forma}" if contenedor else "Desconocido",
                        'necesario': receta.cantidad,
                        'disponible': contenedor.stock if contenedor else 0
                    })
        
        return jsonify({
            'success': True,
            'disponible': disponible,
            'faltantes': faltantes,
            'mensaje': 'Stock suficiente' if disponible else 'Stock insuficiente'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/estimar-costo', methods=['POST'])
def estimar_costo():
    """Estimar costo de un pedido personalizado (para WhatsApp)"""
    try:
        data = request.json
        flores_solicitadas = data.get('flores', [])
        contenedor_id = data.get('contenedor_id')
        
        costo_total = 0
        desglose = []
        
        # Calcular costo de flores
        for flor_data in flores_solicitadas:
            tipo = flor_data.get('tipo')
            color = flor_data.get('color')
            cantidad = flor_data.get('cantidad', 0)
            
            # Buscar la flor más económica con stock disponible
            flor = Flor.query.filter_by(
                tipo=tipo, 
                color=color
            ).filter(
                Flor.cantidad_stock >= cantidad
            ).order_by(
                Flor.costo_unitario.asc()
            ).first()
            
            if flor:
                costo_flor = float(flor.costo_unitario) * cantidad
                costo_total += costo_flor
                desglose.append({
                    'tipo': 'Flor',
                    'nombre': f"{flor.tipo} {flor.color}",
                    'cantidad': cantidad,
                    'costo_unitario': float(flor.costo_unitario),
                    'costo_total': costo_flor
                })
            else:
                return jsonify({
                    'success': False,
                    'error': f"No hay stock suficiente de {tipo} {color}"
                }), 400
        
        # Agregar costo del contenedor
        if contenedor_id:
            contenedor = Contenedor.query.get(contenedor_id)
            if contenedor and contenedor.stock > 0:
                costo_contenedor = float(contenedor.costo)
                costo_total += costo_contenedor
                desglose.append({
                    'tipo': 'Contenedor',
                    'nombre': f"{contenedor.tipo} {contenedor.forma}",
                    'cantidad': 1,
                    'costo_unitario': costo_contenedor,
                    'costo_total': costo_contenedor
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Contenedor no disponible'
                }), 400
        
        # Calcular precio de venta sugerido (margen del 150%)
        precio_sugerido = costo_total * 2.5
        
        return jsonify({
            'success': True,
            'costo_insumos': round(costo_total, 2),
            'precio_sugerido': round(precio_sugerido, 2),
            'margen_porcentaje': 150,
            'desglose': desglose
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

