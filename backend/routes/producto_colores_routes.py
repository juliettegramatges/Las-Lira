"""
Rutas para gestionar colores y flores de productos
"""

from flask import Blueprint, request, jsonify
from app import db
from models.producto_detallado import ProductoColor, ProductoColorFlor
from models.producto import Producto
from models.inventario import Flor

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
                    'hay_stock_suficiente': cf_dict['flor_disponible'] >= color.cantidad_flores_sugerida,
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


@bp.route('/<producto_id>/guardar-receta-completa', methods=['POST'])
def guardar_receta_completa(producto_id):
    """
    Guarda la configuración completa del recetario desde el simulador.
    Actualiza colores, flores asociadas, flores predeterminadas y precio de venta.
    
    Body esperado:
    {
        "colores": [
            {
                "id": "color-123" o "nuevo-timestamp",
                "nombre_color": "Rojo",
                "cantidad_flores_sugerida": 12,
                "flores": [
                    {
                        "flor_id": "FL001",
                        "es_predeterminada": true
                    }
                ]
            }
        ],
        "precio_venta": 25000
    }
    """
    try:
        data = request.get_json()
        
        # Validar producto existe
        producto = Producto.query.get(producto_id)
        if not producto:
            return jsonify({'success': False, 'error': 'Producto no encontrado'}), 404
        
        colores_nuevos = data.get('colores', [])
        precio_venta = data.get('precio_venta')
        
        # Validar que haya al menos un color
        if not colores_nuevos or len(colores_nuevos) == 0:
            return jsonify({'success': False, 'error': 'Debe haber al menos un color'}), 400
        
        # ===== PASO 1: Actualizar precio de venta =====
        if precio_venta is not None:
            producto.precio_venta = precio_venta
        
        # ===== PASO 2: Obtener colores existentes =====
        colores_existentes = ProductoColor.query.filter_by(
            producto_id=producto_id,
            activo=True
        ).all()
        
        # Mapear por ID para fácil acceso
        colores_existentes_map = {str(c.id): c for c in colores_existentes}
        
        # IDs de colores en la nueva configuración
        colores_nuevos_ids = set()
        
        # ===== PASO 3: Crear/actualizar colores =====
        orden = 0
        for color_data in colores_nuevos:
            color_id = str(color_data.get('id', ''))
            es_nuevo = color_id.startswith('nuevo-')
            
            if es_nuevo:
                # Crear nuevo color
                nuevo_color = ProductoColor(
                    producto_id=producto_id,
                    nombre_color=color_data.get('nombre_color', 'Sin nombre'),
                    cantidad_flores_sugerida=color_data.get('cantidad_flores_sugerida', 12),
                    orden=orden
                )
                db.session.add(nuevo_color)
                db.session.flush()  # Para obtener el ID
                
                color_obj = nuevo_color
                color_id_real = nuevo_color.id
            else:
                # Actualizar color existente
                color_obj = colores_existentes_map.get(color_id)
                if color_obj:
                    color_obj.nombre_color = color_data.get('nombre_color', color_obj.nombre_color)
                    color_obj.cantidad_flores_sugerida = color_data.get('cantidad_flores_sugerida', color_obj.cantidad_flores_sugerida)
                    color_obj.orden = orden
                    color_id_real = color_obj.id
                else:
                    continue  # Color no encontrado, saltar
            
            colores_nuevos_ids.add(str(color_id_real))
            
            # ===== PASO 4: Actualizar flores del color =====
            flores_data = color_data.get('flores', [])
            
            # Desactivar todas las flores actuales del color
            ProductoColorFlor.query.filter_by(
                producto_color_id=color_id_real
            ).update({'activo': False, 'es_predeterminada': False})
            
            # Agregar/reactivar flores
            for flor_data in flores_data:
                flor_id = flor_data.get('flor_id')
                es_predeterminada = flor_data.get('es_predeterminada', False)
                
                # Buscar si ya existe esta asociación
                color_flor_existente = ProductoColorFlor.query.filter_by(
                    producto_color_id=color_id_real,
                    flor_id=flor_id
                ).first()
                
                if color_flor_existente:
                    # Reactivar
                    color_flor_existente.activo = True
                    color_flor_existente.es_predeterminada = es_predeterminada
                else:
                    # Crear nueva
                    nueva_color_flor = ProductoColorFlor(
                        producto_color_id=color_id_real,
                        flor_id=flor_id,
                        es_predeterminada=es_predeterminada
                    )
                    db.session.add(nueva_color_flor)
            
            orden += 1
        
        # ===== PASO 5: Desactivar colores que ya no están =====
        for color_id_existente, color_obj in colores_existentes_map.items():
            if str(color_obj.id) not in colores_nuevos_ids:
                color_obj.activo = False
        
        # ===== COMMIT =====
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Receta de {producto.nombre} guardada exitosamente',
            'data': {
                'producto_id': producto_id,
                'colores_actualizados': len(colores_nuevos),
                'precio_venta': float(producto.precio_venta) if producto.precio_venta else 0
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error al guardar receta: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Error al guardar: {str(e)}'}), 500

