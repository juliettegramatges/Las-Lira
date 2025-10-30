"""
Rutas para gestión de inventario (flores y contenedores)
"""

from flask import Blueprint, request, jsonify
from extensions import db
from models.inventario import Flor, Contenedor, Bodega, Proveedor

bp = Blueprint('inventario', __name__)

# ===== FLORES =====

@bp.route('/flores/asignar-precios-sugeridos', methods=['POST'])
def asignar_precios_sugeridos_flores():
    """Asigna precios unitarios sugeridos por tipo a flores con costo 0 o null.
    Los valores son aproximados del mercado por tallo en CLP.
    """
    try:
        precios = {
            'Rosa': 1200,
            'Rosa Premium': 1800,
            'Clavel': 500,
            'Clavelina': 400,
            'Lirio': 2200,
            'Alstroemeria': 800,
            'Girasol': 1500,
            'Gerbera': 1000,
            'Crisantemo': 700,
            'Tulipán': 1800,
            'Hortensia': 3500,
            'Eucalipto': 600,
            'Helecho': 500,
            'Hypericum': 900,
            'Astromelia': 800,
            'Limonium': 600,
        }
        actualizados = 0
        flores = Flor.query.all()
        for f in flores:
            if not f.costo_unitario or float(f.costo_unitario) == 0:
                # buscar por coincidencia en tipo
                valor = None
                for clave, precio in precios.items():
                    if f.tipo and clave.lower() in f.tipo.lower():
                        valor = precio
                        break
                if valor is None:
                    # default genérico
                    valor = 900
                f.costo_unitario = float(valor)
                actualizados += 1
        db.session.commit()
        return jsonify({'success': True, 'actualizados': actualizados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/flores/asignar-stock-sugerido', methods=['POST'])
def asignar_stock_sugerido_flores():
    """Asigna stock total sugerido por tipo a flores con stock 0.
    Valores razonables por rotación aproximada.
    """
    try:
        stock_map = {
            'Clavel': 50,
            'Clavelina': 60,
            'Alstroemeria': 40,
            'Astromelia': 40,
            'Rosa Premium': 24,
            'Rosa': 30,
            'Gerbera': 24,
            'Girasol': 18,
            'Lirio': 18,
            'Tulipán': 18,
            'Crisantemo': 30,
            'Hortensia': 12,
            'Eucalipto': 60,
            'Helecho': 40,
            'Hypericum': 24,
            'Limonium': 40,
            'Anémona': 20,
            'Amaryllis': 12,
        }
        actualizados = 0
        flores = Flor.query.all()
        for f in flores:
            if (f.cantidad_stock or 0) == 0:
                sugerido = None
                for clave, val in stock_map.items():
                    if f.tipo and clave.lower() in f.tipo.lower():
                        sugerido = val
                        break
                if sugerido is None:
                    sugerido = 20
                f.cantidad_stock = int(sugerido)
                actualizados += 1
        db.session.commit()
        return jsonify({'success': True, 'actualizados': actualizados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

# ===== CONTENEDORES: precios/stock sugeridos =====

@bp.route('/contenedores/asignar-precios-sugeridos', methods=['POST'])
def asignar_precios_sugeridos_contenedores():
    """Asigna costos sugeridos a contenedores sin costo, por tipo/material."""
    try:
        precios = {
            'Florero vidrio': 3500,
            'Vidrio': 3000,
            'Cerámica': 4500,
            'Gres': 5000,
            'Madera': 4000,
            'Canasto': 3800,
            'Macetero': 4200,
            'Plástico': 1500,
            'Metal': 3800,
            'Barro': 5000,
        }
        actualizados = 0
        for c in Contenedor.query.all():
            if not c.costo or float(c.costo) == 0:
                candidato = None
                base = f"{(c.tipo or '')} {(c.material or '')}".strip()
                for clave, val in precios.items():
                    if clave.lower() in base.lower():
                        candidato = val
                        break
                if candidato is None:
                    candidato = 3000
                c.costo = float(candidato)
                actualizados += 1
        db.session.commit()
        return jsonify({'success': True, 'actualizados': actualizados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/contenedores/asignar-stock-sugerido', methods=['POST'])
def asignar_stock_sugerido_contenedores():
    """Asigna stock sugerido a contenedores con stock 0, por tipo."""
    try:
        stock_map = {
            'Florero': 20,
            'Vidrio': 24,
            'Cerámica': 12,
            'Madera': 10,
            'Canasto': 16,
            'Macetero': 18,
            'Plástico': 30,
            'Metal': 12,
            'Barro': 12,
        }
        actualizados = 0
        for c in Contenedor.query.all():
            if (c.cantidad_stock or 0) == 0:
                base = f"{(c.tipo or '')} {(c.material or '')}".strip()
                sugerido = None
                for clave, val in stock_map.items():
                    if clave.lower() in base.lower():
                        sugerido = val
                        break
                if sugerido is None:
                    sugerido = 12
                c.cantidad_stock = int(sugerido)
                actualizados += 1
        db.session.commit()
        return jsonify({'success': True, 'actualizados': actualizados})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

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


@bp.route('/flores/<flor_id>', methods=['PATCH'])
def actualizar_flor(flor_id):
    """Actualizar cualquier campo de una flor"""
    try:
        flor = Flor.query.get(flor_id)
        if not flor:
            return jsonify({'success': False, 'error': 'Flor no encontrada'}), 404
        
        data = request.json
        
        # Actualizar campos permitidos
        if 'cantidad_stock' in data:
            flor.cantidad_stock = int(data['cantidad_stock'])
        if 'cantidad_en_uso' in data:
            flor.cantidad_en_uso = int(data['cantidad_en_uso'])
        if 'cantidad_en_evento' in data:
            flor.cantidad_en_evento = int(data['cantidad_en_evento'])
        if 'ubicacion' in data:
            flor.ubicacion = data['ubicacion']
        if 'costo_unitario' in data:
            flor.costo_unitario = float(data['costo_unitario'])
        if 'color' in data:
            flor.color = data['color']
        
        from datetime import date
        flor.fecha_actualizacion = date.today()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': flor.to_dict(),
            'message': 'Flor actualizada correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
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


@bp.route('/contenedores/<contenedor_id>', methods=['PATCH'])
def actualizar_contenedor(contenedor_id):
    """Actualizar cualquier campo de un contenedor"""
    try:
        contenedor = Contenedor.query.get(contenedor_id)
        if not contenedor:
            return jsonify({'success': False, 'error': 'Contenedor no encontrado'}), 404
        
        data = request.json
        
        # Actualizar campos permitidos
        if 'cantidad_stock' in data:
            contenedor.cantidad_stock = int(data['cantidad_stock'])
        if 'cantidad_en_uso' in data:
            contenedor.cantidad_en_uso = int(data['cantidad_en_uso'])
        if 'cantidad_en_evento' in data:
            contenedor.cantidad_en_evento = int(data['cantidad_en_evento'])
        if 'ubicacion' in data:
            contenedor.ubicacion = data['ubicacion']
        if 'costo' in data:
            contenedor.costo = float(data['costo'])
        
        from datetime import date
        contenedor.fecha_actualizacion = date.today()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': contenedor.to_dict(),
            'message': 'Contenedor actualizado correctamente'
        })
        
    except Exception as e:
        db.session.rollback()
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

