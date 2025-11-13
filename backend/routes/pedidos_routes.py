"""
Rutas para gestión de pedidos (Refactorizado)
Las rutas ahora delegan la lógica de negocio al PedidosService
"""

import os
from flask import Blueprint, request, jsonify, session
from services.pedidos_service import PedidosService
from extensions import db
from utils.auditoria_helper import registrar_accion
from routes.auth_routes import require_auth

bp = Blueprint('pedidos', __name__)


@bp.route('/', methods=['GET'], strict_slashes=False)
def listar_pedidos():
    """Listar pedidos con filtros opcionales y paginación"""
    try:
        # Recoger parámetros
        filtros = {
            'estado': request.args.get('estado'),
            'canal': request.args.get('canal'),
            'fecha_desde': request.args.get('fecha_desde'),
            'fecha_hasta': request.args.get('fecha_hasta')
        }
        buscar = request.args.get('buscar', '').strip()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))

        # Delegar al servicio
        pedidos, total, total_pages = PedidosService.listar_pedidos(filtros, buscar, page, limit)

        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in pedidos],
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': total_pages
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/pagados', methods=['GET'], strict_slashes=False)
def listar_pagados():
    """Listar pedidos pagados con búsqueda y paginación"""
    try:
        buscar = request.args.get('buscar', '').strip()
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))

        # Delegar al servicio
        pedidos, total, total_pages = PedidosService.listar_pagados(buscar, page, limit)

        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in pedidos],
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': total_pages
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>', methods=['GET'])
def obtener_pedido(pedido_id):
    """Obtiene un pedido específico por ID"""
    try:
        pedido = PedidosService.obtener_pedido(pedido_id)

        if not pedido:
            return jsonify({'success': False, 'error': 'Pedido no encontrado'}), 404

        return jsonify({
            'success': True,
            'data': pedido.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/', methods=['POST'], strict_slashes=False)
@require_auth
def crear_pedido():
    """Crear un nuevo pedido"""
    try:
        data = request.json

        # Validar campos requeridos
        campos_requeridos = ['canal', 'cliente_nombre', 'cliente_telefono',
                            'precio_ramo', 'direccion_entrega', 'fecha_entrega']
        for campo in campos_requeridos:
            if campo not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido: {campo}'
                }), 400

        # Delegar al servicio
        success, resultado, mensaje = PedidosService.crear_pedido(data)

        if success:
            # Registrar acción de auditoría
            registrar_accion('crear', 'pedido', resultado.id, {'cliente': resultado.cliente_nombre})
            return jsonify({
                'success': True,
                'data': resultado.to_dict(),
                'message': mensaje
            }), 201
        else:
            return jsonify({'success': False, 'error': mensaje}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>/estado', methods=['PATCH'])
def actualizar_estado(pedido_id):
    """Actualiza el estado de un pedido"""
    try:
        data = request.json
        nuevo_estado = data.get('estado')

        if not nuevo_estado:
            return jsonify({'success': False, 'error': 'Estado requerido'}), 400

        # Delegar al servicio
        success, resultado, mensaje = PedidosService.actualizar_estado(pedido_id, nuevo_estado)

        if success:
            # Registrar acción de auditoría
            registrar_accion('cambiar_estado', 'pedido', pedido_id, {'estado_nuevo': nuevo_estado})
            return jsonify({
                'success': True,
                'data': resultado.to_dict(),
                'message': mensaje
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 404 if 'no encontrado' in mensaje else 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>/cancelar', methods=['PATCH'])
def cancelar_pedido(pedido_id):
    """Cancela un pedido y devuelve el stock"""
    try:
        data = request.json or {}
        motivo = data.get('motivo_cancelacion')

        # Delegar al servicio
        success, resultado, mensaje = PedidosService.cancelar_pedido(pedido_id, motivo)

        if success:
            # Registrar acción de auditoría
            registrar_accion('cancelar', 'pedido', pedido_id, {'motivo': motivo})
            return jsonify({
                'success': True,
                'data': resultado.to_dict(),
                'message': mensaje
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 404 if 'no encontrado' in mensaje else 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>', methods=['DELETE'])
@require_auth
def eliminar_pedido(pedido_id):
    """Elimina un pedido"""
    try:
        # Delegar al servicio
        success, mensaje = PedidosService.eliminar_pedido(pedido_id)

        if success:
            # Registrar acción de auditoría
            registrar_accion('eliminar', 'pedido', pedido_id)
            return jsonify({
                'success': True,
                'message': mensaje
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 404 if 'no encontrado' in mensaje else 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<int:pedido_id>', methods=['PUT'])
@require_auth
def actualizar_pedido(pedido_id):
    """Actualiza un pedido existente"""
    try:
        data = request.json

        # Delegar al servicio
        success, resultado, mensaje = PedidosService.actualizar_pedido(pedido_id, data)

        if success:
            # Registrar acción de auditoría
            registrar_accion('actualizar', 'pedido', pedido_id, {
                'cliente': resultado.cliente_nombre if resultado else None,
                'campos_actualizados': list(data.keys()) if data else []
            })
            return jsonify({
                'success': True,
                'data': resultado.to_dict(),
                'message': mensaje
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 404 if 'no encontrado' in mensaje else 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/tablero', methods=['GET'])
def obtener_tablero():
    """Obtiene pedidos organizados para vista Kanban"""
    try:
        from extensions import db
        # Forzar refresh de la sesión para evitar datos en caché
        db.session.expire_all()
        
        # Convertir incluir_despachados a booleano
        incluir_despachados = request.args.get('incluir_despachados', 'false').lower() == 'true'

        # Número de semanas de despachados a mostrar (por defecto 1 semana = 7 días)
        semanas_despachados = int(request.args.get('semanas_despachados', '1'))

        filtros = {
            'estado': request.args.get('estado'),
            'dia_entrega': request.args.get('dia_entrega'),
            'estado_pago': request.args.get('estado_pago'),
            'tipo_pedido': request.args.get('tipo_pedido'),
            'incluir_despachados': incluir_despachados,
            'semanas_despachados': semanas_despachados
        }

        # Delegar al servicio
        tablero = PedidosService.obtener_pedidos_tablero(filtros)

        return jsonify({
            'success': True,
            'data': tablero
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>/cobranza', methods=['PATCH'], strict_slashes=False)
def actualizar_cobranza(pedido_id):
    """Actualiza información de cobranza de un pedido"""
    try:
        data = request.json

        # Delegar al servicio
        success, resultado, mensaje = PedidosService.actualizar_cobranza(pedido_id, data)

        if success:
            # Registrar acción de auditoría
            registrar_accion('actualizar', 'cobranza', pedido_id, {
                'estado_pago': data.get('estado_pago'),
                'metodo_pago': data.get('metodo_pago'),
                'documento_tributario': data.get('documento_tributario')
            })
            return jsonify({
                'success': True,
                'data': resultado.to_dict(),
                'message': mensaje
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 404 if 'no encontrado' in mensaje else 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/resumen-cobranza', methods=['GET'], strict_slashes=False)
def obtener_resumen_cobranza():
    """Obtiene resumen de cobranza"""
    try:
        # Delegar al servicio
        resumen = PedidosService.obtener_resumen_cobranza()

        return jsonify({
            'success': True,
            'data': resumen
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/actualizar-estados-por-fecha', methods=['POST'], strict_slashes=False)
def actualizar_estados_por_fecha():
    """Actualiza automáticamente los estados de pedidos según su fecha de entrega"""
    try:
        # Delegar al servicio
        success, cantidad, mensaje = PedidosService.actualizar_estados_por_fecha()

        if success:
            return jsonify({
                'success': True,
                'actualizados': cantidad,
                'message': mensaje
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<pedido_id>/foto-respaldo', methods=['POST'])
def subir_foto_respaldo(pedido_id):
    """Sube una foto de respaldo para un producto del pedido"""
    try:
        from werkzeug.utils import secure_filename
        from models.pedido import PedidoProducto
        import time

        # Obtener el pedido_producto_id del form data (opcional)
        pedido_producto_id = request.form.get('pedido_producto_id')

        # Verificar que hay un archivo
        if 'imagen' not in request.files:
            return jsonify({'success': False, 'error': 'No se envió ningún archivo'}), 400

        file = request.files['imagen']

        if file.filename == '':
            return jsonify({'success': False, 'error': 'Nombre de archivo vacío'}), 400

        # Validar extensión
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS):
            return jsonify({'success': False, 'error': 'Tipo de archivo no permitido'}), 400

        # Crear carpeta de uploads si no existe
        UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

        # Guardar archivo con nombre seguro
        timestamp = int(time.time())
        filename = secure_filename(f"pedido_{pedido_id}_{timestamp}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Si se especificó pedido_producto_id, actualizar ese producto
        # Si no, actualizar el primer producto del pedido
        if pedido_producto_id:
            pedido_producto = PedidoProducto.query.filter_by(
                id=pedido_producto_id,
                pedido_id=pedido_id
            ).first()
        else:
            # Si no se especifica, usar el primer producto
            pedido_producto = PedidoProducto.query.filter_by(pedido_id=pedido_id).first()

        if not pedido_producto:
            return jsonify({'success': False, 'error': 'Producto del pedido no encontrado'}), 404

        # Actualizar foto_respaldo
        pedido_producto.foto_respaldo = filename
        db.session.commit()

        return jsonify({
            'success': True,
            'filename': filename,
            'url': f'/api/upload/imagen/{filename}',
            'pedido_producto_id': pedido_producto.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ============================================
# ENDPOINTS PARA GESTIÓN DE RUTAS
# ============================================

@bp.route('/rutas', methods=['GET'])
def obtener_rutas():
    """Obtiene pedidos agrupados por comuna para planificar rutas"""
    try:
        from datetime import datetime, timedelta

        # Parámetros de filtro
        filtro_fecha = request.args.get('fecha', 'hoy')  # 'hoy', 'manana', 'YYYY-MM-DD'

        # Calcular fecha objetivo
        hoy = datetime.now().date()
        if filtro_fecha == 'hoy':
            fecha_objetivo = hoy
        elif filtro_fecha == 'manana':
            fecha_objetivo = hoy + timedelta(days=1)
        else:
            try:
                fecha_objetivo = datetime.strptime(filtro_fecha, '%Y-%m-%d').date()
            except:
                fecha_objetivo = hoy

        # Delegar al servicio
        success, rutas, mensaje = PedidosService.obtener_rutas_por_comuna(fecha_objetivo)

        if success:
            return jsonify({
                'success': True,
                'data': rutas,
                'fecha': fecha_objetivo.isoformat()
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/rutas/retiro-tienda', methods=['GET'], strict_slashes=False)
def obtener_retiro_tienda():
    """Obtiene pedidos con retiro en tienda para una fecha específica"""
    try:
        from datetime import datetime, timedelta

        # Parámetros de filtro
        filtro_fecha = request.args.get('fecha', 'hoy')

        # Calcular fecha objetivo
        hoy = datetime.now().date()
        if filtro_fecha == 'hoy':
            fecha_objetivo = hoy
        elif filtro_fecha == 'manana':
            fecha_objetivo = hoy + timedelta(days=1)
        else:
            try:
                fecha_objetivo = datetime.strptime(filtro_fecha, '%Y-%m-%d').date()
            except:
                fecha_objetivo = hoy

        # Delegar al servicio
        success, pedidos, mensaje = PedidosService.obtener_pedidos_retiro_tienda(fecha_objetivo)

        if success:
            return jsonify({
                'success': True,
                'data': pedidos,
                'fecha': fecha_objetivo.isoformat(),
                'total': len(pedidos)
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/<int:pedido_id>/urgente', methods=['PATCH'])
def marcar_urgente(pedido_id):
    """Marca o desmarca un pedido como urgente"""
    try:
        data = request.json
        es_urgente = data.get('es_urgente', True)

        # Delegar al servicio
        success, pedido, mensaje = PedidosService.marcar_urgente(pedido_id, es_urgente)

        if success:
            return jsonify({
                'success': True,
                'data': pedido.to_dict(),
                'message': mensaje
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 404 if 'no encontrado' in mensaje else 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/marcar-despachados', methods=['POST'])
def marcar_despachados():
    """Marca múltiples pedidos como despachados"""
    try:
        data = request.json
        pedidos_ids = data.get('pedidos_ids', [])

        if not pedidos_ids or not isinstance(pedidos_ids, list):
            return jsonify({'success': False, 'error': 'Se requiere array de IDs de pedidos'}), 400

        # Delegar al servicio
        success, resultado, mensaje = PedidosService.marcar_multiples_despachados(pedidos_ids)

        if success:
            return jsonify({
                'success': True,
                'data': resultado,
                'message': mensaje
            })
        else:
            return jsonify({'success': False, 'error': mensaje}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/documento-repartidor', methods=['GET'])
def generar_documento_repartidor():
    """Genera documento imprimible para el repartidor"""
    try:
        from datetime import datetime, timedelta
        from flask import send_file
        from io import BytesIO

        # Parámetros
        filtro_fecha = request.args.get('fecha', 'hoy')
        formato = request.args.get('formato', 'html')  # 'html', 'json' o 'pdf'

        # Calcular fecha objetivo
        hoy = datetime.now().date()
        if filtro_fecha == 'hoy':
            fecha_objetivo = hoy
        elif filtro_fecha == 'manana':
            fecha_objetivo = hoy + timedelta(days=1)
        else:
            try:
                fecha_objetivo = datetime.strptime(filtro_fecha, '%Y-%m-%d').date()
            except:
                fecha_objetivo = hoy

        # Delegar al servicio
        success, documento, mensaje = PedidosService.generar_documento_repartidor(fecha_objetivo)

        if success:
            if formato == 'pdf':
                # Generar PDF
                html = PedidosService.generar_html_documento_repartidor(documento, fecha_objetivo)
                pdf_bytes = PedidosService.generar_pdf_desde_html(html)
                
                filename = f"ruta_repartidor_{fecha_objetivo.strftime('%Y%m%d')}.pdf"
                return send_file(
                    BytesIO(pdf_bytes),
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=filename
                )
            elif formato == 'html':
                # Generar HTML imprimible
                html = PedidosService.generar_html_documento_repartidor(documento, fecha_objetivo)
                return html, 200, {'Content-Type': 'text/html; charset=utf-8'}
            else:
                return jsonify({
                    'success': True,
                    'data': documento,
                    'fecha': fecha_objetivo.isoformat()
                })
        else:
            return jsonify({'success': False, 'error': mensaje}), 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
