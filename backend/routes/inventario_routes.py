"""
Rutas para gestión de inventario (flores y contenedores)
"""

from flask import Blueprint, request, jsonify
from extensions import db
from models.inventario import Flor, Contenedor, Bodega, Proveedor
from config.precios_sugeridos import obtener_precio_flor
from config.stock_sugerido import obtener_stock_flor

bp = Blueprint('inventario', __name__)

# ===== FLORES =====

@bp.route('/flores/asignar-precios-sugeridos', methods=['POST'])
def asignar_precios_sugeridos_flores():
    """
    Asigna precios unitarios sugeridos por tipo a flores con costo 0 o null.
    Los valores son aproximados del mercado por tallo en CLP.
    """
    try:
        actualizados = 0
        flores = Flor.query.all()

        for flor in flores:
            if not flor.costo_unitario or float(flor.costo_unitario) == 0:
                precio_sugerido = obtener_precio_flor(flor.tipo)
                flor.costo_unitario = float(precio_sugerido)
                actualizados += 1

        db.session.commit()
        return jsonify({'success': True, 'actualizados': actualizados})

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/flores/asignar-stock-sugerido', methods=['POST'])
def asignar_stock_sugerido_flores():
    """
    Asigna stock total sugerido por tipo a flores con stock 0.
    Valores razonables por rotación aproximada.
    """
    try:
        actualizados = 0
        flores = Flor.query.all()

        for flor in flores:
            if (flor.cantidad_stock or 0) == 0:
                stock_sugerido = obtener_stock_flor(flor.tipo)
                flor.cantidad_stock = int(stock_sugerido)
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
        from config.precios_sugeridos import obtener_precio_contenedor

        actualizados = 0
        contenedores = Contenedor.query.all()

        for contenedor in contenedores:
            if not contenedor.costo or float(contenedor.costo) == 0:
                tipo_completo = f"{contenedor.tipo or ''} {contenedor.material or ''}".strip()
                precio_sugerido = obtener_precio_contenedor(tipo_completo)
                contenedor.costo = float(precio_sugerido)
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
        from config.stock_sugerido import obtener_stock_contenedor

        actualizados = 0
        contenedores = Contenedor.query.all()

        for contenedor in contenedores:
            if (contenedor.cantidad_stock or 0) == 0:
                tipo_completo = f"{contenedor.tipo or ''} {contenedor.material or ''}".strip()
                stock_sugerido = obtener_stock_contenedor(tipo_completo)
                contenedor.cantidad_stock = int(stock_sugerido)
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


@bp.route('/flores', methods=['POST'])
def crear_flor():
    """Crear una nueva flor"""
    try:
        data = request.json

        # Validar campos requeridos
        if not data.get('tipo'):
            return jsonify({'success': False, 'error': 'Campo requerido: tipo'}), 400

        # Generar ID automático (FL + número secuencial)
        ultima_flor = Flor.query.order_by(Flor.id.desc()).first()
        if ultima_flor and ultima_flor.id.startswith('FL'):
            try:
                ultimo_num = int(ultima_flor.id[2:])
                nuevo_id = f'FL{str(ultimo_num + 1).zfill(3)}'
            except:
                nuevo_id = f'FL{str(Flor.query.count() + 1).zfill(3)}'
        else:
            nuevo_id = f'FL{str(Flor.query.count() + 1).zfill(3)}'

        # Crear flor
        nueva_flor = Flor(
            id=nuevo_id,
            tipo=data['tipo'],
            color=data.get('color', ''),
            nombre=data.get('nombre') or f"{data['tipo']} {data.get('color', '')}".strip(),
            ubicacion=data.get('ubicacion', 'Taller'),
            foto_url=data.get('foto_url'),
            proveedor_id=data.get('proveedor_id'),
            costo_unitario=data.get('costo_unitario', 0),
            cantidad_stock=data.get('cantidad_stock', 0),
            cantidad_en_uso=0,
            cantidad_en_evento=0,
            unidad=data.get('unidad', 'Tallos')
        )

        db.session.add(nueva_flor)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': nueva_flor.to_dict(),
            'message': f'Flor "{nueva_flor.nombre}" creada exitosamente'
        }), 201

    except Exception as e:
        db.session.rollback()
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


@bp.route('/contenedores', methods=['POST'])
def crear_contenedor():
    """Crear un nuevo contenedor"""
    try:
        data = request.json

        # Validar campos requeridos
        if not data.get('tipo'):
            return jsonify({'success': False, 'error': 'Campo requerido: tipo'}), 400

        # Generar ID automático (CT + número secuencial)
        ultimo_contenedor = Contenedor.query.order_by(Contenedor.id.desc()).first()
        if ultimo_contenedor and ultimo_contenedor.id.startswith('CT'):
            try:
                ultimo_num = int(ultimo_contenedor.id[2:])
                nuevo_id = f'CT{str(ultimo_num + 1).zfill(3)}'
            except:
                nuevo_id = f'CT{str(Contenedor.query.count() + 1).zfill(3)}'
        else:
            nuevo_id = f'CT{str(Contenedor.query.count() + 1).zfill(3)}'

        # Generar nombre si no se proporciona
        nombre_auto = f"{data['tipo']} {data.get('material', '')} {data.get('tamano', '')}".strip()

        # Crear contenedor
        nuevo_contenedor = Contenedor(
            id=nuevo_id,
            nombre=data.get('nombre') or nombre_auto,
            tipo=data['tipo'],
            material=data.get('material', ''),
            forma=data.get('forma', ''),
            tamano=data.get('tamano', ''),
            color=data.get('color', ''),
            ubicacion=data.get('ubicacion', 'Bodega 1'),
            foto_url=data.get('foto_url'),
            costo=data.get('costo', 0),
            cantidad_stock=data.get('cantidad_stock', 0),
            cantidad_en_uso=0,
            cantidad_en_evento=0,
            bodega_id=data.get('bodega_id')
        )

        db.session.add(nuevo_contenedor)
        db.session.commit()

        return jsonify({
            'success': True,
            'data': nuevo_contenedor.to_dict(),
            'message': f'Contenedor "{nuevo_contenedor.nombre}" creado exitosamente'
        }), 201

    except Exception as e:
        db.session.rollback()
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

