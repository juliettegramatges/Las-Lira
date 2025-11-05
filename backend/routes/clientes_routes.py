"""
Rutas API para gestión de clientes
"""

from flask import Blueprint, request, jsonify
from extensions import db
from models.cliente import Cliente
from utils.telefono_helpers import normalizar_telefono
from datetime import datetime
from sqlalchemy import or_
import unicodedata

bp = Blueprint('clientes', __name__)

@bp.route('/', methods=['GET'])
def listar_clientes():
    """Listar clientes con paginación"""
    try:
        tipo = request.args.get('tipo')
        buscar = request.args.get('buscar', '').strip()
        etiquetas_str = request.args.get('etiquetas', '').strip()
        
        # Parámetros de paginación
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))
        
        query = Cliente.query
        
        # Filtrar por etiquetas si se especifica
        if etiquetas_str:
            etiqueta_ids = [int(e) for e in etiquetas_str.split(',') if e.isdigit()]
            if etiqueta_ids:
                # Filtrar clientes que tengan AL MENOS UNA de las etiquetas seleccionadas
                # Convertir a string para usar directamente en SQL (seguro porque ya validamos que son int)
                etiquetas_sql = ','.join(map(str, etiqueta_ids))
                sql_query = f'''
                    SELECT DISTINCT cliente_id 
                    FROM cliente_etiquetas 
                    WHERE etiqueta_id IN ({etiquetas_sql})
                '''
                subquery = db.session.execute(db.text(sql_query))
                cliente_ids = [row[0] for row in subquery]
                if cliente_ids:
                    query = query.filter(Cliente.id.in_(cliente_ids))
                else:
                    # Si no hay clientes con esas etiquetas, devolver vacío
                    query = query.filter(Cliente.id.in_([]))
        
        if tipo:
            query = query.filter_by(tipo_cliente=tipo)
        
        if buscar:
            query = query.filter(
                (Cliente.nombre.ilike(f'%{buscar}%')) |
                (Cliente.telefono.ilike(f'%{buscar}%')) |
                (Cliente.email.ilike(f'%{buscar}%'))
            )
        
        # Contar total antes de paginar
        total = query.count()
        
        # Aplicar paginación
        clientes = query.order_by(Cliente.nombre).limit(limit).offset((page - 1) * limit).all()
        
        # Calcular estadísticas globales de TODOS los clientes (sin filtros)
        total_global = Cliente.query.count()
        
        # Calcular promedios de gasto y pedidos por tipo de cliente
        from sqlalchemy import func
        
        def calcular_promedio_gasto(tipo):
            resultado = db.session.query(func.avg(Cliente.total_gastado)).filter_by(tipo_cliente=tipo).scalar()
            return float(resultado) if resultado else 0
        
        def calcular_promedio_pedidos(tipo):
            resultado = db.session.query(func.avg(Cliente.total_pedidos)).filter_by(tipo_cliente=tipo).scalar()
            return float(resultado) if resultado else 0
        
        stats = {
            'total': total_global,
            'vip': Cliente.query.filter_by(tipo_cliente='VIP').count(),
            'fiel': Cliente.query.filter_by(tipo_cliente='Fiel').count(),
            'nuevo': Cliente.query.filter_by(tipo_cliente='Nuevo').count(),
            'ocasional': Cliente.query.filter_by(tipo_cliente='Ocasional').count(),
            'promedio_vip': calcular_promedio_gasto('VIP'),
            'promedio_fiel': calcular_promedio_gasto('Fiel'),
            'promedio_nuevo': calcular_promedio_gasto('Nuevo'),
            'promedio_ocasional': calcular_promedio_gasto('Ocasional'),
            'promedio_pedidos_vip': calcular_promedio_pedidos('VIP'),
            'promedio_pedidos_fiel': calcular_promedio_pedidos('Fiel'),
            'promedio_pedidos_nuevo': calcular_promedio_pedidos('Nuevo'),
            'promedio_pedidos_ocasional': calcular_promedio_pedidos('Ocasional'),
        }
        
        return jsonify({
            'success': True,
            'data': [c.to_dict() for c in clientes],
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit,
            'stats': stats  # Estadísticas globales
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


@bp.route('/buscar-por-telefono', methods=['GET'])
def buscar_por_telefono():
    """Buscar cliente por número de teléfono (para compatibilidad)"""
    try:
        telefono_original = request.args.get('telefono', '').strip()
        
        if not telefono_original:
            return jsonify({'success': False, 'error': 'Teléfono requerido'}), 400
        
        # Normalizar el teléfono que viene del frontend
        telefono_normalizado = normalizar_telefono(telefono_original)
        
        # Buscar comparando teléfonos normalizados
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


@bp.route('/buscar-por-nombre', methods=['GET'])
def buscar_por_nombre():
    """Buscar clientes por nombre (búsqueda inteligente)"""
    try:
        termino = request.args.get('nombre', '').strip()

        if not termino or len(termino) < 2:
            return jsonify({'success': True, 'clientes': []})

        def normalizar(texto: str) -> str:
            if not texto:
                return ''
            # Eliminar acentos y normalizar espacios
            texto = ''.join(
                ch for ch in unicodedata.normalize('NFKD', texto)
                if not unicodedata.combining(ch)
            )
            return ' '.join(texto.lower().split())

        termino_norm = normalizar(termino)

        # Traer un conjunto razonable y filtrar en Python para soporte sin acentos en SQLite
        candidatos = Cliente.query.order_by(Cliente.total_pedidos.desc()).limit(1000).all()

        resultados = []
        for c in candidatos:
            nombre_c = normalizar(c.nombre)
            email_c = normalizar(getattr(c, 'email', '') or '')
            tel_c = normalizar(getattr(c, 'telefono', '') or '')

            if (
                termino_norm in nombre_c or
                termino_norm in email_c or
                termino_norm in tel_c
            ):
                resultados.append(c)

        # Si no hay resultados, relajar: buscar por cada palabra
        if not resultados:
            partes = termino_norm.split()
            for c in candidatos:
                texto = ' '.join([
                    normalizar(c.nombre),
                    normalizar(getattr(c, 'email', '') or ''),
                    normalizar(getattr(c, 'telefono', '') or ''),
                ])
                if all(p in texto for p in partes):
                    resultados.append(c)

        # Limitar y ordenar por total de pedidos desc
        resultados = sorted(resultados, key=lambda x: getattr(x, 'total_pedidos', 0), reverse=True)[:15]

        return jsonify({
            'success': True,
            'clientes': [c.to_dict() for c in resultados],
            'total': len(resultados)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@bp.route('/etiquetas', methods=['GET'])
def obtener_etiquetas():
    """Obtener todas las etiquetas disponibles agrupadas por categoría"""
    try:
        result = db.session.execute(db.text('''
            SELECT id, nombre, categoria, descripcion, color, icono, orden
            FROM etiquetas_cliente
            WHERE activa = 1
            ORDER BY orden
        '''))
        
        etiquetas_por_categoria = {}
        
        for row in result:
            etiqueta = {
                'id': row[0],
                'nombre': row[1],
                'categoria': row[2],
                'descripcion': row[3],
                'color': row[4],
                'icono': row[5],
                'orden': row[6]
            }
            
            categoria = etiqueta['categoria']
            if categoria not in etiquetas_por_categoria:
                etiquetas_por_categoria[categoria] = []
            
            etiquetas_por_categoria[categoria].append(etiqueta)
        
        return jsonify({
            'success': True,
            'data': etiquetas_por_categoria
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


@bp.route('/<cliente_id>/pedidos', methods=['GET'])
def obtener_historial_pedidos(cliente_id):
    """Obtener historial de pedidos de un cliente"""
    try:
        from models.pedido import Pedido
        
        cliente = Cliente.query.get(cliente_id)
        if not cliente:
            return jsonify({'success': False, 'error': 'Cliente no encontrado'}), 404
        
        # Obtener pedidos ordenados por fecha (más recientes primero)
        pedidos = Pedido.query.filter_by(cliente_id=cliente_id).order_by(Pedido.fecha_pedido.desc()).all()
        
        return jsonify({
            'success': True,
            'data': {
                'cliente': cliente.to_dict(),
                'pedidos': [pedido.to_dict() for pedido in pedidos],
                'total_pedidos': len(pedidos)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

