"""
Rutas API para gestión de clientes
"""

from flask import Blueprint, request, jsonify
from backend.app import db
from backend.models.cliente import Cliente
from datetime import datetime

bp = Blueprint('clientes', __name__)

@bp.route('/', methods=['GET'])
def listar_clientes():
    """Listar todos los clientes"""
    try:
        tipo = request.args.get('tipo')
        buscar = request.args.get('buscar', '').strip()
        
        query = Cliente.query
        
        if tipo:
            query = query.filter_by(tipo_cliente=tipo)
        
        if buscar:
            query = query.filter(
                (Cliente.nombre.ilike(f'%{buscar}%')) |
                (Cliente.telefono.ilike(f'%{buscar}%')) |
                (Cliente.email.ilike(f'%{buscar}%'))
            )
        
        clientes = query.order_by(Cliente.nombre).all()
        
        return jsonify({
            'success': True,
            'data': [c.to_dict() for c in clientes],
            'total': len(clientes)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<cliente_id>', methods=['GET'])
def obtener_cliente(cliente_id):
    """Obtener detalles de un cliente"""
    try:
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'data': cliente.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/', methods=['POST'])
def crear_cliente():
    """Crear un nuevo cliente"""
    try:
        data = request.json
        
        # Validar que el teléfono no exista
        telefono_existente = Cliente.query.filter_by(telefono=data['telefono']).first()
        if telefono_existente:
            return jsonify({
                'success': False, 
                'error': 'Ya existe un cliente con ese número de teléfono',
                'cliente_existente': telefono_existente.to_dict()
            }), 400
        
        # Generar ID del cliente
        ultimo_cliente = Cliente.query.order_by(Cliente.id.desc()).first()
        if ultimo_cliente:
            numero = int(ultimo_cliente.id[3:]) + 1
            nuevo_id = f"CLI{numero:03d}"
        else:
            nuevo_id = "CLI001"
        
        # Crear cliente
        cliente = Cliente(
            id=nuevo_id,
            nombre=data['nombre'],
            telefono=data['telefono'],
            email=data.get('email'),
            tipo_cliente=data.get('tipo_cliente', 'Nuevo'),
            direccion_principal=data.get('direccion_principal'),
            notas=data.get('notas')
        )
        
        db.session.add(cliente)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': cliente.to_dict(),
            'message': f'Cliente {nuevo_id} creado exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<cliente_id>', methods=['PUT'])
def actualizar_cliente(cliente_id):
    """Actualizar información de un cliente"""
    try:
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
        
        data = request.json
        
        # Actualizar campos
        if 'nombre' in data:
            cliente.nombre = data['nombre']
        if 'telefono' in data:
            # Verificar que no exista otro cliente con ese teléfono
            otro_cliente = Cliente.query.filter(
                Cliente.telefono == data['telefono'],
                Cliente.id != cliente_id
            ).first()
            if otro_cliente:
                return jsonify({
                    'success': False, 
                    'error': 'Ya existe otro cliente con ese número de teléfono'
                }), 400
            cliente.telefono = data['telefono']
        if 'email' in data:
            cliente.email = data['email']
        if 'tipo_cliente' in data:
            cliente.tipo_cliente = data['tipo_cliente']
        if 'direccion_principal' in data:
            cliente.direccion_principal = data['direccion_principal']
        if 'notas' in data:
            cliente.notas = data['notas']
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': cliente.to_dict(),
            'message': 'Cliente actualizado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<cliente_id>', methods=['DELETE'])
def eliminar_cliente(cliente_id):
    """Eliminar un cliente (soft delete - solo si no tiene pedidos)"""
    try:
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
        
        # Verificar si tiene pedidos
        if cliente.total_pedidos > 0:
            return jsonify({
                'success': False, 
                'error': f'No se puede eliminar el cliente porque tiene {cliente.total_pedidos} pedido(s) asociado(s)'
            }), 400
        
        db.session.delete(cliente)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cliente eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


def normalizar_telefono(telefono):
    """Normalizar número de teléfono (quitar espacios, guiones, paréntesis)"""
    import re
    return re.sub(r'[\s\-\(\)]', '', telefono)


@bp.route('/buscar-por-telefono', methods=['GET'])
def buscar_por_telefono():
    """Buscar cliente por número de teléfono"""
    try:
        telefono_original = request.args.get('telefono', '').strip()
        
        if not telefono_original:
            return jsonify({'success': False, 'error': 'Teléfono requerido'}), 400
        
        # Normalizar el teléfono que viene del frontend
        telefono_normalizado = normalizar_telefono(telefono_original)
        
        # Buscar comparando teléfonos normalizados
        # Esto permite encontrar "+56912345678" aunque se busque "+56 9 1234 5678"
        todos_clientes = Cliente.query.all()
        cliente = None
        
        for c in todos_clientes:
            if normalizar_telefono(c.telefono) == telefono_normalizado:
                cliente = c
                break
        
        if cliente:
            return jsonify({
                'success': True,
                'encontrado': True,
                'data': cliente.to_dict()
            })
        else:
            return jsonify({
                'success': True,
                'encontrado': False,
                'data': None,
                'message': 'Cliente no encontrado. Se creará uno nuevo al guardar el pedido.'
            })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/estadisticas', methods=['GET'])
def estadisticas_clientes():
    """Obtener estadísticas generales de clientes"""
    try:
        total = Cliente.query.count()
        por_tipo = db.session.query(
            Cliente.tipo_cliente,
            db.func.count(Cliente.id)
        ).group_by(Cliente.tipo_cliente).all()
        
        return jsonify({
            'success': True,
            'data': {
                'total_clientes': total,
                'por_tipo': {tipo: count for tipo, count in por_tipo},
                'top_clientes': [
                    c.to_dict() for c in Cliente.query.order_by(
                        Cliente.total_gastado.desc()
                    ).limit(10).all()
                ]
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

