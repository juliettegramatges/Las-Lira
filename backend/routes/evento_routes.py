"""
Rutas para gestión de eventos
"""

from flask import Blueprint, request, jsonify
from extensions import db
from models.evento import Evento, EventoInsumo, ProductoEvento
from models.inventario import Flor, Contenedor
from models.producto import Producto
from models.cliente import Cliente
from datetime import datetime
from sqlalchemy import or_

bp = Blueprint('eventos', __name__)


@bp.route('/', methods=['GET'])
def obtener_eventos():
    """Obtiene todos los eventos"""
    try:
        eventos = Evento.query.order_by(Evento.fecha_evento.desc()).all()
        return jsonify({
            'success': True,
            'data': [evento.to_dict() for evento in eventos]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<evento_id>', methods=['GET'])
def obtener_evento(evento_id):
    """Obtiene un evento específico con sus insumos"""
    try:
        evento = Evento.query.get(evento_id)
        if not evento:
            return jsonify({'success': False, 'error': 'Evento no encontrado'}), 404
        
        evento_dict = evento.to_dict()
        evento_dict['insumos'] = [insumo.to_dict() for insumo in evento.insumos]
        
        return jsonify({
            'success': True,
            'data': evento_dict
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/', methods=['POST'])
def crear_evento():
    """Crea un nuevo evento (Cotización)"""
    try:
        data = request.get_json()
        
        # Generar ID del evento
        ultimo_evento = Evento.query.order_by(Evento.id.desc()).first()
        if ultimo_evento and ultimo_evento.id.startswith('EV'):
            numero = int(ultimo_evento.id[2:]) + 1
        else:
            numero = 1
        nuevo_id = f'EV{numero:03d}'
        
        nuevo_evento = Evento(
            id=nuevo_id,
            cliente_nombre=data.get('cliente_nombre'),
            cliente_telefono=data.get('cliente_telefono'),
            cliente_email=data.get('cliente_email'),
            nombre_evento=data.get('nombre_evento'),
            tipo_evento=data.get('tipo_evento'),
            fecha_evento=datetime.fromisoformat(data['fecha_evento']) if data.get('fecha_evento') else None,
            hora_evento=data.get('hora_evento'),
            lugar_evento=data.get('lugar_evento'),
            cantidad_personas=data.get('cantidad_personas', 0),
            estado='Cotización',
            margen_porcentaje=data.get('margen_porcentaje', 30),
            notas_cotizacion=data.get('notas_cotizacion')
        )
        
        db.session.add(nuevo_evento)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': nuevo_evento.to_dict(),
            'message': 'Evento creado exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<evento_id>', methods=['PUT'])
def actualizar_evento(evento_id):
    """Actualiza un evento existente"""
    try:
        evento = Evento.query.get(evento_id)
        if not evento:
            return jsonify({'success': False, 'error': 'Evento no encontrado'}), 404
        
        data = request.get_json()
        
        # Actualizar campos permitidos
        if 'cliente_nombre' in data:
            evento.cliente_nombre = data['cliente_nombre']
        if 'cliente_telefono' in data:
            evento.cliente_telefono = data['cliente_telefono']
        if 'cliente_email' in data:
            evento.cliente_email = data['cliente_email']
        if 'nombre_evento' in data:
            evento.nombre_evento = data['nombre_evento']
        if 'tipo_evento' in data:
            evento.tipo_evento = data['tipo_evento']
        if 'fecha_evento' in data:
            evento.fecha_evento = datetime.fromisoformat(data['fecha_evento']) if data['fecha_evento'] else None
        if 'hora_evento' in data:
            evento.hora_evento = data['hora_evento']
        if 'lugar_evento' in data:
            evento.lugar_evento = data['lugar_evento']
        if 'cantidad_personas' in data:
            evento.cantidad_personas = data['cantidad_personas']
        if 'costo_mano_obra' in data:
            evento.costo_mano_obra = data['costo_mano_obra']
        if 'costo_transporte' in data:
            evento.costo_transporte = data['costo_transporte']
        if 'costo_otros' in data:
            evento.costo_otros = data['costo_otros']
        if 'margen_porcentaje' in data:
            evento.margen_porcentaje = data['margen_porcentaje']
        if 'notas_cotizacion' in data:
            evento.notas_cotizacion = data['notas_cotizacion']
        if 'notas_internas' in data:
            evento.notas_internas = data['notas_internas']
        
        # Recalcular costos y precios
        recalcular_costos_evento(evento)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': evento.to_dict(),
            'message': 'Evento actualizado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<evento_id>/insumos', methods=['POST'])
def agregar_insumo(evento_id):
    """Agrega un insumo al evento"""
    try:
        evento = Evento.query.get(evento_id)
        if not evento:
            return jsonify({'success': False, 'error': 'Evento no encontrado'}), 404
        
        data = request.get_json()
        tipo_insumo = data.get('tipo_insumo')
        
        nuevo_insumo = EventoInsumo(
            evento_id=evento_id,
            tipo_insumo=tipo_insumo,
            cantidad=data.get('cantidad', 1),
            costo_unitario=data.get('costo_unitario', 0),
            notas=data.get('notas')
        )
        
        # Asignar referencia según tipo
        if tipo_insumo == 'flor':
            nuevo_insumo.flor_id = data.get('flor_id')
        elif tipo_insumo == 'contenedor':
            nuevo_insumo.contenedor_id = data.get('contenedor_id')
        elif tipo_insumo == 'producto':
            nuevo_insumo.producto_id = data.get('producto_id')
        elif tipo_insumo == 'producto_evento':
            nuevo_insumo.producto_evento_id = data.get('producto_evento_id')
        elif tipo_insumo == 'otro':
            nuevo_insumo.nombre_otro = data.get('nombre_otro')
        
        # Calcular costo total
        nuevo_insumo.costo_total = nuevo_insumo.cantidad * nuevo_insumo.costo_unitario
        
        db.session.add(nuevo_insumo)
        
        # Recalcular costos del evento
        recalcular_costos_evento(evento)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': nuevo_insumo.to_dict(),
            'message': 'Insumo agregado exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<evento_id>/insumos/<int:insumo_id>', methods=['DELETE'])
def eliminar_insumo(evento_id, insumo_id):
    """Elimina un insumo del evento"""
    try:
        insumo = EventoInsumo.query.get(insumo_id)
        if not insumo or insumo.evento_id != evento_id:
            return jsonify({'success': False, 'error': 'Insumo no encontrado'}), 404
        
        db.session.delete(insumo)
        
        # Recalcular costos del evento
        evento = Evento.query.get(evento_id)
        recalcular_costos_evento(evento)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Insumo eliminado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<evento_id>/estado', methods=['PUT'])
def cambiar_estado(evento_id):
    """Cambia el estado del evento"""
    try:
        evento = Evento.query.get(evento_id)
        if not evento:
            return jsonify({'success': False, 'error': 'Evento no encontrado'}), 404
        
        data = request.get_json()
        nuevo_estado = data.get('estado')
        
        # Validar transiciones de estado
        estados_validos = ['Cotización', 'Propuesta Enviada', 'Confirmado', 
                          'En Preparación', 'En Evento', 'Finalizado', 'Retirado']
        
        if nuevo_estado not in estados_validos:
            return jsonify({'success': False, 'error': 'Estado inválido'}), 400
        
        estado_anterior = evento.estado
        evento.estado = nuevo_estado
        
        # Actualizar fechas según el estado
        if nuevo_estado == 'Propuesta Enviada' and not evento.fecha_propuesta:
            evento.fecha_propuesta = datetime.utcnow()
        elif nuevo_estado == 'Confirmado' and not evento.fecha_confirmacion:
            evento.fecha_confirmacion = datetime.utcnow()
        elif nuevo_estado == 'Finalizado' and not evento.fecha_finalizacion:
            evento.fecha_finalizacion = datetime.utcnow()
        elif nuevo_estado == 'Retirado' and not evento.fecha_retiro:
            evento.fecha_retiro = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': evento.to_dict(),
            'message': f'Estado cambiado de {estado_anterior} a {nuevo_estado}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<evento_id>/reservar-insumos', methods=['POST'])
def reservar_insumos(evento_id):
    """Reserva los insumos del evento (incrementa cantidad_en_evento)"""
    try:
        evento = Evento.query.get(evento_id)
        if not evento:
            return jsonify({'success': False, 'error': 'Evento no encontrado'}), 404
        
        if evento.insumos_reservados:
            return jsonify({'success': False, 'error': 'Insumos ya reservados'}), 400
        
        # Validar stock disponible
        errores = []
        for insumo in evento.insumos:
            if insumo.tipo_insumo == 'flor':
                flor = Flor.query.get(insumo.flor_id)
                if flor and flor.cantidad_disponible < insumo.cantidad:
                    errores.append(f'{flor.tipo} {flor.color}: necesitas {insumo.cantidad}, disponible {flor.cantidad_disponible}')
            
            elif insumo.tipo_insumo == 'contenedor':
                contenedor = Contenedor.query.get(insumo.contenedor_id)
                if contenedor and contenedor.cantidad_disponible < insumo.cantidad:
                    errores.append(f'{contenedor.tipo}: necesitas {insumo.cantidad}, disponible {contenedor.cantidad_disponible}')
            
            elif insumo.tipo_insumo == 'producto_evento':
                prod_evento = ProductoEvento.query.get(insumo.producto_evento_id)
                if prod_evento and prod_evento.cantidad_disponible < insumo.cantidad:
                    errores.append(f'{prod_evento.nombre}: necesitas {insumo.cantidad}, disponible {prod_evento.cantidad_disponible}')
        
        if errores:
            return jsonify({
                'success': False,
                'error': 'Stock insuficiente',
                'detalles': errores
            }), 400
        
        # Reservar insumos
        for insumo in evento.insumos:
            if insumo.tipo_insumo == 'flor':
                flor = Flor.query.get(insumo.flor_id)
                if flor:
                    flor.cantidad_en_evento += insumo.cantidad
                    insumo.reservado = True
            
            elif insumo.tipo_insumo == 'contenedor':
                contenedor = Contenedor.query.get(insumo.contenedor_id)
                if contenedor:
                    contenedor.cantidad_en_evento += insumo.cantidad
                    insumo.reservado = True
            
            elif insumo.tipo_insumo == 'producto_evento':
                prod_evento = ProductoEvento.query.get(insumo.producto_evento_id)
                if prod_evento:
                    prod_evento.cantidad_en_evento += insumo.cantidad
                    insumo.reservado = True
        
        evento.insumos_reservados = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Insumos reservados exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<evento_id>/descontar-stock', methods=['POST'])
def descontar_stock(evento_id):
    """Descuenta el stock de los insumos reservados"""
    try:
        evento = Evento.query.get(evento_id)
        if not evento:
            return jsonify({'success': False, 'error': 'Evento no encontrado'}), 404
        
        if not evento.insumos_reservados:
            return jsonify({'success': False, 'error': 'Primero debes reservar los insumos'}), 400
        
        if evento.insumos_descontados:
            return jsonify({'success': False, 'error': 'Stock ya descontado'}), 400
        
        # Descontar stock
        for insumo in evento.insumos:
            if insumo.tipo_insumo == 'flor':
                flor = Flor.query.get(insumo.flor_id)
                if flor:
                    flor.cantidad_stock -= insumo.cantidad
                    insumo.descontado_stock = True
            
            elif insumo.tipo_insumo == 'contenedor':
                contenedor = Contenedor.query.get(insumo.contenedor_id)
                if contenedor:
                    contenedor.stock -= insumo.cantidad
                    insumo.descontado_stock = True
            
            elif insumo.tipo_insumo == 'producto_evento':
                prod_evento = ProductoEvento.query.get(insumo.producto_evento_id)
                if prod_evento:
                    prod_evento.cantidad_stock -= insumo.cantidad
                    insumo.descontado_stock = True
        
        evento.insumos_descontados = True
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Stock descontado exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<evento_id>/marcar-devuelto', methods=['POST'])
def marcar_devuelto(evento_id):
    """Marca insumos como devueltos y libera las reservas"""
    try:
        evento = Evento.query.get(evento_id)
        if not evento:
            return jsonify({'success': False, 'error': 'Evento no encontrado'}), 404
        
        data = request.get_json()
        devoluciones = data.get('devoluciones', [])  # [{insumo_id, cantidad_devuelta}]
        
        insumos_faltantes = []
        
        for devolucion in devoluciones:
            insumo = EventoInsumo.query.get(devolucion['insumo_id'])
            if not insumo or insumo.evento_id != evento_id:
                continue
            
            cantidad_devuelta = devolucion.get('cantidad_devuelta', 0)
            cantidad_faltante = insumo.cantidad - cantidad_devuelta
            
            if cantidad_devuelta == insumo.cantidad:
                # Todo devuelto
                insumo.devuelto = True
                insumo.cantidad_faltante = 0
            else:
                # Hay faltantes
                insumo.devuelto = False
                insumo.cantidad_faltante = cantidad_faltante
                insumos_faltantes.append({
                    'nombre': insumo.to_dict()['nombre'],
                    'cantidad_faltante': cantidad_faltante
                })
            
            # Liberar reserva
            if insumo.tipo_insumo == 'flor':
                flor = Flor.query.get(insumo.flor_id)
                if flor:
                    flor.cantidad_en_evento -= insumo.cantidad
            
            elif insumo.tipo_insumo == 'contenedor':
                contenedor = Contenedor.query.get(insumo.contenedor_id)
                if contenedor:
                    contenedor.cantidad_en_evento -= insumo.cantidad
            
            elif insumo.tipo_insumo == 'producto_evento':
                prod_evento = ProductoEvento.query.get(insumo.producto_evento_id)
                if prod_evento:
                    prod_evento.cantidad_en_evento -= insumo.cantidad
        
        # Actualizar evento
        if insumos_faltantes:
            evento.insumos_faltantes = True
            evento.lista_faltantes = str(insumos_faltantes)
        else:
            evento.insumos_faltantes = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Devoluciones registradas exitosamente',
            'faltantes': insumos_faltantes
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# =====================================
# FUNCIONES AUXILIARES
# =====================================

def recalcular_costos_evento(evento):
    """Recalcula los costos totales y precios del evento"""
    # Calcular costo de insumos
    costo_insumos = sum(insumo.costo_total for insumo in evento.insumos)
    evento.costo_insumos = costo_insumos
    
    # Calcular costo total
    evento.costo_total = (
        float(evento.costo_insumos or 0) +
        float(evento.costo_mano_obra or 0) +
        float(evento.costo_transporte or 0) +
        float(evento.costo_otros or 0)
    )
    
    # Calcular precio propuesta con margen
    margen_decimal = float(evento.margen_porcentaje or 30) / 100
    evento.precio_propuesta = evento.costo_total / (1 - margen_decimal)
    
    # Si no hay precio final, usar propuesta
    if not evento.precio_final or evento.precio_final == 0:
        evento.precio_final = evento.precio_propuesta
    
    # Calcular saldo
    evento.saldo = float(evento.precio_final or 0) - float(evento.anticipo or 0)


# =====================================
# PRODUCTOS DE EVENTOS
# =====================================

@bp.route('/productos-evento', methods=['GET'])
def obtener_productos_evento():
    """Obtiene todos los productos de eventos"""
    try:
        productos = ProductoEvento.query.filter_by(activo=True).all()
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in productos]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

