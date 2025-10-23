"""
Rutas para gestión de productos y catálogo
"""

from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models.producto import Producto, RecetaProducto
from backend.models.inventario import Flor, Contenedor

bp = Blueprint('productos', __name__)

@bp.route('/', methods=['GET'])
def listar_productos():
    """Listar todos los productos"""
    try:
        disponible_shopify = request.args.get('disponible_shopify', type=bool)
        activo = request.args.get('activo', type=bool, default=True)
        
        query = Producto.query
        
        if disponible_shopify is not None:
            query = query.filter_by(disponible_shopify=disponible_shopify)
        if activo is not None:
            query = query.filter_by(activo=activo)
        
        productos = query.order_by(Producto.nombre).all()
        
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in productos],
            'total': len(productos)
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

