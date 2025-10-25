"""
Rutas para gestión de pedidos
"""

from flask import Blueprint, request, jsonify
from extensions import db
from models.pedido import Pedido, PedidoInsumo
from models.cliente import Cliente
from config.plazos_pago import obtener_plazo_pago
from utils.fecha_helpers import clasificar_pedido
from datetime import datetime, timedelta

bp = Blueprint('pedidos', __name__)

@bp.route('/', methods=['GET'], strict_slashes=False)
def listar_pedidos():
    """Listar pedidos con filtros opcionales y paginación"""
    try:
        # Parámetros de filtro
        estado = request.args.get('estado')
        canal = request.args.get('canal')
        fecha_desde = request.args.get('fecha_desde')
        fecha_hasta = request.args.get('fecha_hasta')
        
        # Parámetros de paginación
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))
        
        query = Pedido.query
        
        if estado:
            query = query.filter_by(estado=estado)
        if canal:
            query = query.filter_by(canal=canal)
        if fecha_desde:
            query = query.filter(Pedido.fecha_pedido >= datetime.fromisoformat(fecha_desde))
        if fecha_hasta:
            query = query.filter(Pedido.fecha_pedido <= datetime.fromisoformat(fecha_hasta))
        
        # Contar total antes de paginar
        total = query.count()
        
        # Aplicar paginación
        pedidos = query.order_by(Pedido.fecha_pedido.desc()).limit(limit).offset((page - 1) * limit).all()
        
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in pedidos],
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>', methods=['GET'])
def obtener_pedido(pedido_id):
    """Obtener detalles de un pedido específico"""
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        
        return jsonify({
            'success': True,
            'data': pedido.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def normalizar_telefono(telefono):
    """Normalizar número de teléfono (quitar espacios, guiones, paréntesis)"""
    import re
    return re.sub(r'[\s\-\(\)]', '', telefono)


@bp.route('/', methods=['POST'], strict_slashes=False)
def crear_pedido():
    """Crear un nuevo pedido"""
    try:
        data = request.json
        
        # Normalizar teléfono
        telefono_original = data['cliente_telefono']
        telefono_normalizado = normalizar_telefono(telefono_original)
        
        # Gestionar cliente (buscar o crear)
        cliente_id = data.get('cliente_id')
        cliente = None
        
        if cliente_id:
            # Cliente ya existe, usar ese
            cliente = Cliente.query.get(cliente_id)
        else:
            # Buscar por teléfono normalizado
            todos_clientes = Cliente.query.all()
            for c in todos_clientes:
                if normalizar_telefono(c.telefono) == telefono_normalizado:
                    cliente = c
                    break
            
            if not cliente:
                # Cliente no existe, crear uno nuevo
                ultimo_cliente = Cliente.query.order_by(Cliente.id.desc()).first()
                if ultimo_cliente:
                    numero = int(ultimo_cliente.id[3:]) + 1
                    nuevo_cliente_id = f"CLI{numero:03d}"
                else:
                    nuevo_cliente_id = "CLI001"
                
                cliente = Cliente(
                    id=nuevo_cliente_id,
                    nombre=data['cliente_nombre'],
                    telefono=telefono_normalizado,  # Guardar teléfono normalizado
                    email=data.get('cliente_email'),
                    tipo_cliente='Nuevo'
                )
                db.session.add(cliente)
                db.session.flush()  # Para obtener el ID
        
        # Generar ID del pedido
        ultimo_pedido = Pedido.query.order_by(Pedido.id.desc()).first()
        if ultimo_pedido:
            numero = int(ultimo_pedido.id[3:]) + 1
            nuevo_id = f"PED{numero:03d}"
        else:
            nuevo_id = "PED001"
        
        # Calcular plazo de pago
        # Si viene manual en el request, usar ese; sino calcularlo por tipo de cliente
        if 'plazo_pago_dias' in data:
            plazo_pago = int(data['plazo_pago_dias'])
        elif cliente:
            plazo_pago = obtener_plazo_pago(cliente.tipo_cliente)
        else:
            plazo_pago = 0  # Sin cliente, pago inmediato
        
        # Parsear fecha de entrega
        fecha_entrega = datetime.fromisoformat(data['fecha_entrega'].replace('Z', '+00:00'))
        
        # 🚀 CLASIFICACIÓN AUTOMÁTICA: Determinar estado y día según fecha de entrega
        clasificacion = clasificar_pedido(fecha_entrega)
        
        # 💰 CALCULAR FECHA MÁXIMA DE PAGO
        # Si tiene plazo de pago, calcular fecha límite
        fecha_maxima_pago = None
        if plazo_pago > 0:
            # Fecha máxima = fecha del pedido + días de plazo
            fecha_maxima_pago = datetime.utcnow() + timedelta(days=plazo_pago)
        
        # Crear pedido
        pedido = Pedido(
            id=nuevo_id,
            canal=data['canal'],
            shopify_order_number=data.get('shopify_order_number'),
            cliente_id=cliente.id if cliente else None,
            cliente_nombre=data['cliente_nombre'],
            cliente_telefono=telefono_normalizado,  # Guardar teléfono normalizado
            cliente_email=data.get('cliente_email'),
            producto_id=data.get('producto_id'),
            arreglo_pedido=data.get('arreglo_pedido'),
            detalles_adicionales=data.get('detalles_adicionales'),
            precio_ramo=data['precio_ramo'],
            precio_envio=data.get('precio_envio', 0),
            destinatario=data.get('destinatario'),
            mensaje=data.get('mensaje'),
            firma=data.get('firma'),
            direccion_entrega=data['direccion_entrega'],
            comuna=data.get('comuna'),
            motivo=data.get('motivo'),
            plazo_pago_dias=plazo_pago,
            fecha_maxima_pago=fecha_maxima_pago,  # 📅 Fecha límite de pago
            fecha_entrega=fecha_entrega,
            estado=clasificacion['estado'],  # 🎯 Estado automático
            dia_entrega=clasificacion['dia_entrega']  # 📅 Día automático
        )
        
        db.session.add(pedido)
        
        # Actualizar estadísticas del cliente
        if cliente:
            cliente.total_pedidos += 1
            cliente.total_gastado = (cliente.total_gastado or 0) + pedido.precio_total
            cliente.ultima_compra = datetime.now()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': pedido.to_dict(),
            'message': f'Pedido {nuevo_id} creado exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>/estado', methods=['PATCH'])
def actualizar_estado(pedido_id):
    """Actualizar estado de un pedido"""
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        
        data = request.json
        nuevo_estado = data.get('estado')
        
        # Estados válidos del sistema (alineados con el tablero Kanban)
        estados_validos = [
            'Entregas de Hoy',
            'Entregas para Mañana',
            'En Proceso',
            'Listo para Despacho',
            'Despachados',
            'Pedidos Semana',
            'Eventos',
            'Archivado',
            'Cancelado'
        ]
        
        if nuevo_estado not in estados_validos:
            return jsonify({'success': False, 'error': f'Estado inválido. Debe ser uno de: {", ".join(estados_validos)}'}), 400
        
        pedido.estado = nuevo_estado
        
        # 🔥 NUEVO: Actualizar fecha_entrega según la columna a la que se mueve
        from datetime import datetime, timedelta
        from utils.fecha_helpers import obtener_dia_semana
        
        hoy = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        
        # Si se mueve a columnas específicas, actualizar la fecha de entrega
        if nuevo_estado == 'Entregas de Hoy':
            pedido.fecha_entrega = hoy
            print(f"📅 Actualizando fecha_entrega de {pedido.id} → HOY ({hoy.date()})")
        elif nuevo_estado == 'Entregas para Mañana':
            pedido.fecha_entrega = hoy + timedelta(days=1)
            print(f"📅 Actualizando fecha_entrega de {pedido.id} → MAÑANA ({(hoy + timedelta(days=1)).date()})")
        
        # Actualizar etiqueta de día según la fecha (ya actualizada si corresponde)
        if pedido.fecha_entrega:
            dia_calculado = obtener_dia_semana(pedido.fecha_entrega)
            pedido.dia_entrega = dia_calculado
            print(f"🔄 {pedido.id}: estado={nuevo_estado}, fecha_entrega={pedido.fecha_entrega.date()}, dia_entrega={dia_calculado}")
        
        db.session.commit()
        
        pedido_dict = pedido.to_dict()
        print(f"✅ Pedido actualizado: dia_entrega={pedido_dict.get('dia_entrega')}, fecha_entrega={pedido_dict.get('fecha_entrega')}")
        
        return jsonify({
            'success': True,
            'data': pedido_dict,
            'message': f'Estado y fecha actualizados a: {nuevo_estado}'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>', methods=['DELETE'])
def eliminar_pedido(pedido_id):
    """Eliminar (o cancelar) un pedido"""
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        
        # En lugar de eliminar, cambiar estado a Cancelado
        pedido.estado = 'Cancelado'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Pedido {pedido_id} cancelado'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/tablero', methods=['GET'])
def obtener_tablero():
    """Obtener pedidos organizados por estado (formato Kanban estilo Trello Las-Lira)"""
    try:
        # Estados según el flujo del Trello (orden de prioridad)
        estados = [
            'Entregas de Hoy',      # 🔥 Urgente - hoy
            'Entregas para Mañana', # ⚡ Próximo - mañana
            'En Proceso',           # 🔧 Taller trabajando
            'Listo para Despacho',  # ✅ Listo para enviar
            'Despachados',          # 📦 Completados
            'Pedidos Semana',       # 📅 Planificación semanal
            'Eventos'               # 🎉 Pedidos para eventos especiales
        ]
        tablero = {}
        
        for estado in estados:
            if estado == 'Despachados':
                # Combinar Despachados y Archivado en una sola columna
                pedidos = Pedido.query.filter(
                    (Pedido.estado == 'Despachados') | (Pedido.estado == 'Archivado')
                ).order_by(Pedido.fecha_entrega.desc()).limit(50).all()
            else:
                pedidos = Pedido.query.filter_by(estado=estado).order_by(Pedido.fecha_entrega.asc()).all()
            
            tablero[estado] = [p.to_dict() for p in pedidos]
        
        return jsonify({
            'success': True,
            'data': tablero,
            'total_pendientes': sum(len(pedidos) for pedidos in tablero.values())
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>/cobranza', methods=['PATCH'], strict_slashes=False)
def actualizar_cobranza(pedido_id):
    """
    Actualizar estado de cobranza de un pedido
    
    FLUJO EN 3 ETAPAS:
    1. ETAPA 1: estado_pago (Pagado / No Pagado)
    2. ETAPA 2: metodo_pago (solo si está pagado)
    3. ETAPA 3: documento_tributario + numero_documento
    """
    try:
        from config.cobranza import ESTADOS_PAGO, METODOS_PAGO, DOCUMENTOS_TRIBUTARIOS
        
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        
        data = request.json
        
        # 💰 ETAPA 1: Actualizar estado de pago (¿Está pagado?)
        if 'estado_pago' in data:
            if data['estado_pago'] not in ESTADOS_PAGO:
                return jsonify({'success': False, 'error': 'Estado de pago inválido'}), 400
            pedido.estado_pago = data['estado_pago']
            
            # Si cambia a "No Pagado", limpiar método de pago
            if data['estado_pago'] == 'No Pagado':
                pedido.metodo_pago = None
        
        # 💳 ETAPA 2: Actualizar método de pago (solo si está pagado)
        if 'metodo_pago' in data:
            if data['metodo_pago'] and data['metodo_pago'] not in METODOS_PAGO:
                return jsonify({'success': False, 'error': 'Método de pago inválido'}), 400
            pedido.metodo_pago = data['metodo_pago']
            
            # Si se especifica un método de pago, el pedido debe estar marcado como pagado
            if data['metodo_pago']:
                pedido.estado_pago = 'Pagado'
        
        # 🧾 ETAPA 3A: Actualizar documento tributario
        if 'documento_tributario' in data:
            if data['documento_tributario'] not in DOCUMENTOS_TRIBUTARIOS:
                return jsonify({'success': False, 'error': 'Documento inválido'}), 400
            pedido.documento_tributario = data['documento_tributario']
            
            # Si cambia a "Hacer boleta/factura", limpiar número de documento
            if data['documento_tributario'] in ['Hacer boleta', 'Hacer factura']:
                pedido.numero_documento = None
        
        # 🧾 ETAPA 3B: Actualizar número de documento
        if 'numero_documento' in data:
            pedido.numero_documento = data['numero_documento']
            
            # Si se ingresa número de documento, cambiar automáticamente a "emitida"
            if pedido.numero_documento and pedido.numero_documento.strip():
                if pedido.documento_tributario == 'Hacer boleta':
                    pedido.documento_tributario = 'Boleta emitida'
                elif pedido.documento_tributario == 'Hacer factura':
                    pedido.documento_tributario = 'Factura emitida'
        
        pedido.fecha_actualizacion = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': pedido.to_dict(),
            'message': 'Cobranza actualizada exitosamente'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/resumen-cobranza', methods=['GET'], strict_slashes=False)
def resumen_cobranza():
    """Obtener resumen de cobranza pendiente"""
    try:
        # Pedidos sin pagar (ordenados por fecha_pedido descendente - más nuevos primero)
        sin_pagar = Pedido.query.filter(
            Pedido.estado_pago == 'No Pagado',
            Pedido.estado.notin_(['Cancelado', 'Archivado'])
        ).order_by(Pedido.fecha_pedido.desc()).all()
        
        # Pedidos sin documentar (ordenados por fecha_pedido descendente - más nuevos primero)
        sin_documentar = Pedido.query.filter(
            Pedido.documento_tributario.in_(['Hacer boleta', 'Hacer factura', 'Falta boleta o factura']),
            Pedido.estado.notin_(['Cancelado'])
        ).order_by(Pedido.fecha_pedido.desc()).all()
        
        # Calcular totales
        total_sin_pagar = sum((p.precio_ramo or 0) + (p.precio_envio or 0) for p in sin_pagar)
        
        return jsonify({
            'success': True,
            'data': {
                'sin_pagar': {
                    'cantidad': len(sin_pagar),
                    'total': float(total_sin_pagar),
                    'pedidos': [p.to_dict() for p in sin_pagar]
                },
                'sin_documentar': {
                    'cantidad': len(sin_documentar),
                    'pedidos': [p.to_dict() for p in sin_documentar]
                }
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/actualizar-estados-por-fecha', methods=['POST'], strict_slashes=False)
def actualizar_estados_por_fecha():
    """
    Actualiza automáticamente los estados de pedidos según su fecha de entrega
    - Pedidos con fecha pasada → Despachados
    - Pedidos actuales → Clasificación por fecha
    """
    try:
        from datetime import datetime, date
        
        hoy = date.today()
        
        # Estados que pueden ser actualizados (incluye Archivado para convertir a Despachados)
        estados_actualizables = [
            'Pedido', 'Pedidos Semana', 'Entregas para Mañana', 'Entregas de Hoy', 
            'En Proceso', 'Listo para Despacho', 'Archivado'
        ]
        
        pedidos_actualizables = Pedido.query.filter(Pedido.estado.in_(estados_actualizables)).all()
        
        actualizados = 0
        despachados_automaticos = 0
        
        for pedido in pedidos_actualizables:
            # Convertir fecha_entrega a date si es datetime
            fecha_entrega = pedido.fecha_entrega.date() if isinstance(pedido.fecha_entrega, datetime) else pedido.fecha_entrega
            
            # Si la fecha de entrega ya pasó → marcar como Despachados
            if fecha_entrega < hoy:
                if pedido.estado != 'Despachados':
                    pedido.estado = 'Despachados'
                    actualizados += 1
                    despachados_automaticos += 1
            else:
                # Si la fecha es hoy o futura → reclasificar según fecha
                clasificacion = clasificar_pedido(pedido.fecha_entrega)
                
                # Solo actualizar si el estado cambió Y el pedido aún no está en proceso
                if pedido.estado in ['Pedido', 'Pedidos Semana', 'Entregas para Mañana', 'Entregas de Hoy']:
                    if pedido.estado != clasificacion['estado']:
                        pedido.estado = clasificacion['estado']
                        pedido.dia_entrega = clasificacion['dia_entrega']
                        actualizados += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{actualizados} pedidos reclasificados ({despachados_automaticos} marcados como Despachados)',
            'actualizados': actualizados,
            'despachados': despachados_automaticos
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>/foto-respaldo', methods=['POST'])
def subir_foto_respaldo(pedido_id):
    """
    Subir foto de respaldo del arreglo antes del despacho
    """
    try:
        pedido = Pedido.query.get(pedido_id)
        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404
        
        # Verificar que el pedido esté en estado correcto
        if pedido.estado not in ['Listo para Despacho', 'Despachados']:
            return jsonify({
                'success': False, 
                'error': 'Solo se pueden subir fotos de respaldo para pedidos "Listo para Despacho" o "Despachados"'
            }), 400
        
        # Verificar que se envió un archivo
        if 'imagen' not in request.files:
            return jsonify({'success': False, 'error': 'No se envió ninguna imagen'}), 400
        
        archivo = request.files['imagen']
        if archivo.filename == '':
            return jsonify({'success': False, 'error': 'Archivo vacío'}), 400
        
        # Validar tipo de archivo
        extensiones_permitidas = {'png', 'jpg', 'jpeg', 'webp', 'gif'}
        extension = archivo.filename.rsplit('.', 1)[1].lower() if '.' in archivo.filename else ''
        
        if extension not in extensiones_permitidas:
            return jsonify({
                'success': False, 
                'error': 'Formato no permitido. Solo: JPG, PNG, WEBP, GIF'
            }), 400
        
        # Guardar archivo
        import os
        from werkzeug.utils import secure_filename
        
        # Crear directorio si no existe
        upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'fotos_respaldo')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Nombre del archivo: pedido_id_timestamp.extension
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_archivo = f"{pedido_id}_{timestamp}.{extension}"
        ruta_archivo = os.path.join(upload_folder, nombre_archivo)
        
        # Guardar
        archivo.save(ruta_archivo)
        
        # Actualizar pedido
        pedido.foto_enviado_url = nombre_archivo
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Foto de respaldo subida correctamente',
            'foto_url': nombre_archivo
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

