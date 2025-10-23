"""
Rutas para gestión de inventario (flores y contenedores)
"""

from flask import Blueprint, request, jsonify
from app import db
from models.inventario import Flor, Contenedor, Bodega, Proveedor

bp = Blueprint('inventario', __name__)

# ===== FLORES =====

@bp.route('/flores', methods=['GET'])
def listar_flores():
    """Listar todas las flores"""
    try:
        bodega_id = request.args.get('bodega_id', type=int)
        tipo = request.args.get('tipo')
        color = request.args.get('color')
        stock_bajo = request.args.get('stock_bajo', type=bool)
        
        query = Flor.query
        
        if bodega_id:
            query = query.filter_by(bodega_id=bodega_id)
        if tipo:
            query = query.filter_by(tipo=tipo)
        if color:
            query = query.filter_by(color=color)
        if stock_bajo:
            query = query.filter(Flor.cantidad_stock < 20)
        
        flores = query.order_by(Flor.tipo, Flor.color).all()
        
        return jsonify({
            'success': True,
            'data': [f.to_dict() for f in flores],
            'total': len(flores)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/flores/<flor_id>', methods=['GET'])
def obtener_flor(flor_id):
    """Obtener detalles de una flor específica"""
    try:
        flor = Flor.query.get(flor_id)
        if not flor:
            return jsonify({'success': False, 'error': 'Flor no encontrada'}), 404
        
        return jsonify({
            'success': True,
            'data': flor.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/flores/<flor_id>/stock', methods=['PATCH'])
def actualizar_stock_flor(flor_id):
    """Actualizar stock de una flor"""
    try:
        flor = Flor.query.get(flor_id)
        if not flor:
            return jsonify({'success': False, 'error': 'Flor no encontrada'}), 404
        
        data = request.json
        cantidad = data.get('cantidad')
        operacion = data.get('operacion', 'set')  # 'set', 'add', 'subtract'
        
        if operacion == 'set':
            flor.cantidad_stock = cantidad
        elif operacion == 'add':
            flor.cantidad_stock += cantidad
        elif operacion == 'subtract':
            flor.cantidad_stock = max(0, flor.cantidad_stock - cantidad)
        
        from datetime import date
        flor.fecha_actualizacion = date.today()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': flor.to_dict(),
            'message': 'Stock actualizado correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ===== CONTENEDORES =====

@bp.route('/contenedores', methods=['GET'])
def listar_contenedores():
    """Listar todos los contenedores"""
    try:
        bodega_id = request.args.get('bodega_id', type=int)
        tipo = request.args.get('tipo')
        
        query = Contenedor.query
        
        if bodega_id:
            query = query.filter_by(bodega_id=bodega_id)
        if tipo:
            query = query.filter_by(tipo=tipo)
        
        contenedores = query.order_by(Contenedor.tipo, Contenedor.tamano).all()
        
        return jsonify({
            'success': True,
            'data': [c.to_dict() for c in contenedores],
            'total': len(contenedores)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/contenedores/<contenedor_id>/stock', methods=['PATCH'])
def actualizar_stock_contenedor(contenedor_id):
    """Actualizar stock de un contenedor"""
    try:
        contenedor = Contenedor.query.get(contenedor_id)
        if not contenedor:
            return jsonify({'success': False, 'error': 'Contenedor no encontrado'}), 404
        
        data = request.json
        cantidad = data.get('cantidad')
        operacion = data.get('operacion', 'set')
        
        if operacion == 'set':
            contenedor.stock = cantidad
        elif operacion == 'add':
            contenedor.stock += cantidad
        elif operacion == 'subtract':
            contenedor.stock = max(0, contenedor.stock - cantidad)
        
        from datetime import date
        contenedor.fecha_actualizacion = date.today()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': contenedor.to_dict(),
            'message': 'Stock actualizado correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ===== BODEGAS =====

@bp.route('/bodegas', methods=['GET'])
def listar_bodegas():
    """Listar todas las bodegas"""
    try:
        bodegas = Bodega.query.filter_by(activa=True).all()
        
        return jsonify({
            'success': True,
            'data': [b.to_dict() for b in bodegas]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ===== RESUMEN DE INVENTARIO =====

@bp.route('/resumen', methods=['GET'])
def resumen_inventario():
    """Obtener resumen del inventario"""
    try:
        total_flores = db.session.query(db.func.sum(Flor.cantidad_stock)).scalar() or 0
        total_contenedores = db.session.query(db.func.sum(Contenedor.stock)).scalar() or 0
        
        flores_bajo_stock = Flor.query.filter(Flor.cantidad_stock < 20).count()
        contenedores_bajo_stock = Contenedor.query.filter(Contenedor.stock < 5).count()
        
        # Valor total del inventario
        valor_flores = db.session.query(
            db.func.sum(Flor.cantidad_stock * Flor.costo_unitario)
        ).scalar() or 0
        
        valor_contenedores = db.session.query(
            db.func.sum(Contenedor.stock * Contenedor.costo)
        ).scalar() or 0
        
        return jsonify({
            'success': True,
            'data': {
                'total_flores': int(total_flores),
                'total_contenedores': int(total_contenedores),
                'flores_bajo_stock': flores_bajo_stock,
                'contenedores_bajo_stock': contenedores_bajo_stock,
                'valor_total_inventario': float(valor_flores + valor_contenedores),
                'valor_flores': float(valor_flores),
                'valor_contenedores': float(valor_contenedores)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

