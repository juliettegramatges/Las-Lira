"""
Rutas para gestionar colores y flores de productos
"""

from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models.producto_detallado import ProductoColor, ProductoColorFlor
from backend.models.producto import Producto
from backend.models.inventario import Flor

bp = Blueprint('producto_colores', __name__)

@bp.route('/<producto_id>/colores', methods=['GET'])
def obtener_colores_producto(producto_id):
    """Obtiene todos los colores configurados para un producto"""
    try:
        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        colores = ProductoColor.query.filter_by(
            producto_id=producto_id,
            activo=True
        ).order_by(ProductoColor.orden).all()
        
        return jsonify({
            'success': True,
            'data': [color.to_dict() for color in colores]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<producto_id>/colores', methods=['POST'])
def crear_color_producto(producto_id):
    """Crea un nuevo color para un producto"""
    try:
        data = request.get_json()
        
        # Validar producto existe
        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        # Crear color
        color = ProductoColor(
            producto_id=producto_id,
            nombre_color=data.get('nombre_color'),
            cantidad_flores_sugerida=data.get('cantidad_flores_sugerida', 0),
            orden=data.get('orden', 0),
            notas=data.get('notas')
        )
        
        db.session.add(color)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': color.to_dict(),
            'message': 'Color creado exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/colores/<int:color_id>', methods=['PUT'])
def actualizar_color(color_id):
    """Actualiza un color existente"""
    try:
        color = ProductoColor.query.get(color_id)
        if not color:
            return jsonify({'success': False, 'error': 'Color no encontrado'}), 404
        
        data = request.get_json()
        
        if 'nombre_color' in data:
            color.nombre_color = data['nombre_color']
        if 'cantidad_flores_sugerida' in data:
            color.cantidad_flores_sugerida = data['cantidad_flores_sugerida']
        if 'orden' in data:
            color.orden = data['orden']
        if 'notas' in data:
            color.notas = data['notas']
        if 'activo' in data:
            color.activo = data['activo']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': color.to_dict(),
            'message': 'Color actualizado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/colores/<int:color_id>', methods=['DELETE'])
def eliminar_color(color_id):
    """Elimina (desactiva) un color"""
    try:
        color = ProductoColor.query.get(color_id)
        if not color:
            return jsonify({'success': False, 'error': 'Color no encontrado'}), 404
        
        color.activo = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Color eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/colores/<int:color_id>/flores', methods=['POST'])
def agregar_flor_a_color(color_id):
    """Agrega una flor disponible para un color"""
    try:
        data = request.get_json()
        
        # Validar color existe
        color = ProductoColor.query.get(color_id)
        if not color:
            return jsonify({'success': False, 'error': 'Color no encontrado'}), 404
        
        # Validar flor existe
        flor_id = data.get('flor_id')
        flor = Flor.query.get(flor_id)
        if not flor:
            return jsonify({'success': False, 'error': 'Flor no encontrada'}), 404
        
        # Verificar que no exista ya
        existe = ProductoColorFlor.query.filter_by(
            producto_color_id=color_id,
            flor_id=flor_id,
            activo=True
        ).first()
        
        if existe:
            return jsonify({'success': False, 'error': 'Esta flor ya está asociada a este color'}), 400
        
        # Si se marca como predeterminada, quitar flag de las demás
        es_predeterminada = data.get('es_predeterminada', False)
        if es_predeterminada:
            ProductoColorFlor.query.filter_by(
                producto_color_id=color_id
            ).update({'es_predeterminada': False})
        
        # Crear asociación
        color_flor = ProductoColorFlor(
            producto_color_id=color_id,
            flor_id=flor_id,
            es_predeterminada=es_predeterminada,
            notas=data.get('notas')
        )
        
        db.session.add(color_flor)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': color_flor.to_dict(),
            'message': 'Flor agregada exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/colores/flores/<int:color_flor_id>', methods=['DELETE'])
def eliminar_flor_de_color(color_flor_id):
    """Elimina (desactiva) una flor de un color"""
    try:
        color_flor = ProductoColorFlor.query.get(color_flor_id)
        if not color_flor:
            return jsonify({'success': False, 'error': 'Asociación no encontrada'}), 404
        
        color_flor.activo = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Flor eliminada del color exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/colores/flores/<int:color_flor_id>/predeterminada', methods=['PUT'])
def marcar_flor_predeterminada(color_flor_id):
    """Marca una flor como predeterminada para su color"""
    try:
        color_flor = ProductoColorFlor.query.get(color_flor_id)
        if not color_flor:
            return jsonify({'success': False, 'error': 'Asociación no encontrada'}), 404
        
        # Quitar flag de las demás flores del mismo color
        ProductoColorFlor.query.filter_by(
            producto_color_id=color_flor.producto_color_id
        ).update({'es_predeterminada': False})
        
        # Marcar esta como predeterminada
        color_flor.es_predeterminada = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Flor marcada como predeterminada'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<producto_id>/configuracion-completa', methods=['GET'])
def obtener_configuracion_completa(producto_id):
    """
    Obtiene la configuración completa de un producto incluyendo:
    - Datos básicos del producto
    - Colores con sus flores disponibles (con stock y precio)
    - Cálculo de disponibilidad por color
    - Costo estimado usando flores predeterminadas
    """
    try:
        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        colores = ProductoColor.query.filter_by(
            producto_id=producto_id,
            activo=True
        ).order_by(ProductoColor.orden).all()
        
        # Enriquecer cada color con información detallada
        colores_detallados = []
        hay_stock_total = True
        costo_total_estimado = 0
        
        for color in colores:
            flores_disponibles = []
            tiene_stock_color = False
            flor_predeterminada = None
            
            for cf in color.flores_disponibles:
                if not cf.activo:
                    continue
                
                # Convertir a dict y agregar campos adicionales
                cf_dict = cf.to_dict()
                
                flor_info = {
                    **cf_dict,
                    'cantidad_necesaria': color.cantidad_flores_sugerida,
                    'hay_stock_suficiente': cf_dict['flor_stock'] >= color.cantidad_flores_sugerida,
                    'costo_color': float(cf_dict['flor_costo']) * color.cantidad_flores_sugerida
                }
                
                flores_disponibles.append(flor_info)
                
                # Verificar si hay al menos una flor con stock suficiente
                if flor_info['hay_stock_suficiente']:
                    tiene_stock_color = True
                
                # Guardar la predeterminada para el cálculo
                if cf_dict['es_predeterminada']:
                    flor_predeterminada = flor_info
            
            # Si no hay stock para este color, no hay stock total
            if not tiene_stock_color:
                hay_stock_total = False
            
            # Sumar al costo total usando la flor predeterminada
            if flor_predeterminada:
                costo_total_estimado += flor_predeterminada['costo_color']
            
            color_detallado = {
                'id': color.id,
                'nombre_color': color.nombre_color,
                'cantidad_sugerida': color.cantidad_flores_sugerida,
                'orden': color.orden,
                'flores_disponibles': flores_disponibles,
                'tiene_stock': tiene_stock_color
            }
            
            colores_detallados.append(color_detallado)
        
        precio_venta_float = float(producto.precio_venta) if producto.precio_venta else 0
        
        return jsonify({
            'success': True,
            'data': {
                'producto': producto.to_dict(),
                'colores': colores_detallados,
                'tiene_configuracion': len(colores) > 0,
                'hay_stock_completo': hay_stock_total,
                'costo_estimado_flores': costo_total_estimado,
                'precio_venta': precio_venta_float,
                'margen_estimado': precio_venta_float - costo_total_estimado
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

