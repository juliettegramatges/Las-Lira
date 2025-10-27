"""
Rutas API para reportes y analytics
"""

from flask import Blueprint, request, jsonify
from extensions import db
from models.pedido import Pedido
from models.cliente import Cliente
from models.producto import Producto
from datetime import datetime, timedelta
from sqlalchemy import func, extract, case
import json

bp = Blueprint('reportes', __name__)

@bp.route('/kpis', methods=['GET'])
def obtener_kpis():
    """Obtener KPIs principales del dashboard"""
    try:
        # Fecha actual y mes anterior
        hoy = datetime.now()
        primer_dia_mes = hoy.replace(day=1)
        mes_anterior = (primer_dia_mes - timedelta(days=1)).replace(day=1)
        
        # Ventas del mes actual
        ventas_mes = db.session.query(
            func.sum(Pedido.precio_ramo + Pedido.precio_envio)
        ).filter(
            Pedido.fecha_pedido >= primer_dia_mes
        ).scalar() or 0
        
        # Ventas del mes anterior
        ventas_mes_anterior = db.session.query(
            func.sum(Pedido.precio_ramo + Pedido.precio_envio)
        ).filter(
            Pedido.fecha_pedido >= mes_anterior,
            Pedido.fecha_pedido < primer_dia_mes
        ).scalar() or 0
        
        # Pedidos del mes
        pedidos_mes = Pedido.query.filter(
            Pedido.fecha_pedido >= primer_dia_mes
        ).count()
        
        # Pedidos mes anterior
        pedidos_mes_anterior = Pedido.query.filter(
            Pedido.fecha_pedido >= mes_anterior,
            Pedido.fecha_pedido < primer_dia_mes
        ).count()
        
        # Ticket promedio
        ticket_promedio = ventas_mes / pedidos_mes if pedidos_mes > 0 else 0
        
        # Crecimiento
        crecimiento = ((ventas_mes - ventas_mes_anterior) / ventas_mes_anterior * 100) if ventas_mes_anterior > 0 else 0
        
        # Clientes nuevos este mes (primera compra en este mes)
        # Contar clientes cuyo primer pedido fue este mes
        primer_pedido_por_cliente = db.session.query(
            Pedido.cliente_id,
            func.min(Pedido.fecha_pedido).label('primer_pedido')
        ).group_by(Pedido.cliente_id).all()
        
        # Filtrar en Python para obtener los del mes actual y mes anterior
        clientes_nuevos_mes = sum(1 for _, primer_pedido in primer_pedido_por_cliente if primer_pedido >= primer_dia_mes)
        clientes_nuevos_mes_anterior = sum(1 for _, primer_pedido in primer_pedido_por_cliente if mes_anterior <= primer_pedido < primer_dia_mes)
        
        # Crecimiento de clientes nuevos
        crecimiento_clientes = ((clientes_nuevos_mes - clientes_nuevos_mes_anterior) / clientes_nuevos_mes_anterior * 100) if clientes_nuevos_mes_anterior > 0 else (100 if clientes_nuevos_mes > 0 else 0)
        
        # Tasa de entrega a tiempo (pedidos despachados)
        pedidos_despachados = Pedido.query.filter(
            Pedido.fecha_pedido >= primer_dia_mes,
            Pedido.estado == 'Despachados'
        ).count()
        
        tasa_entrega = (pedidos_despachados / pedidos_mes * 100) if pedidos_mes > 0 else 0
        
        return jsonify({
            'success': True,
            'data': {
                'ventas_mes': float(ventas_mes),
                'ventas_mes_anterior': float(ventas_mes_anterior),
                'pedidos_mes': pedidos_mes,
                'pedidos_mes_anterior': pedidos_mes_anterior,
                'ticket_promedio': float(ticket_promedio),
                'crecimiento_ventas': float(crecimiento),
                'clientes_nuevos_mes': clientes_nuevos_mes,
                'clientes_nuevos_mes_anterior': clientes_nuevos_mes_anterior,
                'crecimiento_clientes': float(crecimiento_clientes),
                'tasa_entrega': float(tasa_entrega)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/ventas-mensuales', methods=['GET'])
def ventas_mensuales():
    """Obtener ventas por mes de los últimos 12 meses"""
    try:
        resultado = db.session.query(
            func.strftime('%Y-%m', Pedido.fecha_pedido).label('mes'),
            func.count(Pedido.id).label('pedidos'),
            func.sum(Pedido.precio_ramo + Pedido.precio_envio).label('ventas')
        ).filter(
            Pedido.fecha_pedido >= datetime.now() - timedelta(days=365)
        ).group_by('mes').order_by('mes').all()
        
        datos = [{
            'mes': row.mes,
            'pedidos': row.pedidos,
            'ventas': float(row.ventas) if row.ventas else 0
        } for row in resultado]
        
        return jsonify({'success': True, 'data': datos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/top-productos', methods=['GET'])
def top_productos():
    """Top 10 productos más vendidos (filtrable por mes y año)"""
    try:
        limit = int(request.args.get('limit', 10))
        anio = request.args.get('anio', type=int)  # Cambiado de 'año' a 'anio'
        mes = request.args.get('mes', type=int)
        
        # Construir query base
        query = db.session.query(
            Pedido.arreglo_pedido,
            func.count(Pedido.id).label('cantidad'),
            func.sum(Pedido.precio_ramo).label('ventas')
        ).filter(
            Pedido.arreglo_pedido.isnot(None),
            Pedido.arreglo_pedido != ''
        )
        
        # Aplicar filtros si se especifican
        if anio and mes:
            # Calcular primer y último día del mes
            primer_dia = datetime(anio, mes, 1)
            if mes == 12:
                ultimo_dia = datetime(anio + 1, 1, 1)
            else:
                ultimo_dia = datetime(anio, mes + 1, 1)
            
            query = query.filter(
                Pedido.fecha_pedido >= primer_dia,
                Pedido.fecha_pedido < ultimo_dia
            )
        
        resultado = query.group_by(Pedido.arreglo_pedido).order_by(
            func.count(Pedido.id).desc()
        ).limit(limit).all()
        
        datos = [{
            'producto': row.arreglo_pedido,
            'cantidad': row.cantidad,
            'ventas': float(row.ventas) if row.ventas else 0
        } for row in resultado]
        
        return jsonify({
            'success': True, 
            'data': datos,
            'mes': mes,
            'anio': anio
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/distribucion-tipos', methods=['GET'])
def distribucion_tipos():
    """Distribución por tipo de pedido"""
    try:
        resultado = db.session.query(
            Pedido.tipo_pedido,
            func.count(Pedido.id).label('cantidad')
        ).filter(
            Pedido.tipo_pedido.isnot(None),
            Pedido.tipo_pedido != ''
        ).group_by(Pedido.tipo_pedido).all()
        
        datos = [{
            'tipo': row.tipo_pedido or 'Sin especificar',
            'cantidad': row.cantidad
        } for row in resultado]
        
        return jsonify({'success': True, 'data': datos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/top-clientes', methods=['GET'])
def top_clientes():
    """Top 10 clientes por gasto total"""
    try:
        limit = int(request.args.get('limit', 10))
        
        clientes = Cliente.query.filter(
            Cliente.total_gastado > 0
        ).order_by(Cliente.total_gastado.desc()).limit(limit).all()
        
        datos = [{
            'id': c.id,
            'nombre': c.nombre,
            'total_pedidos': c.total_pedidos,
            'total_gastado': float(c.total_gastado),
            'tipo_cliente': c.tipo_cliente
        } for c in clientes]
        
        return jsonify({'success': True, 'data': datos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/distribucion-clientes', methods=['GET'])
def distribucion_clientes():
    """Distribución de clientes por tipo"""
    try:
        resultado = db.session.query(
            Cliente.tipo_cliente,
            func.count(Cliente.id).label('cantidad')
        ).group_by(Cliente.tipo_cliente).all()
        
        datos = [{
            'tipo': row.tipo_cliente,
            'cantidad': row.cantidad
        } for row in resultado]
        
        return jsonify({'success': True, 'data': datos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/comunas-frecuentes', methods=['GET'])
def comunas_frecuentes():
    """Comunas más frecuentadas"""
    try:
        limit = int(request.args.get('limit', 15))
        
        resultado = db.session.query(
            Pedido.comuna,
            func.count(Pedido.id).label('cantidad'),
            func.sum(Pedido.precio_ramo + Pedido.precio_envio).label('ventas')
        ).filter(
            Pedido.comuna.isnot(None),
            Pedido.comuna != ''
        ).group_by(Pedido.comuna).order_by(
            func.count(Pedido.id).desc()
        ).limit(limit).all()
        
        datos = [{
            'comuna': row.comuna,
            'cantidad': row.cantidad,
            'ventas': float(row.ventas) if row.ventas else 0
        } for row in resultado]
        
        return jsonify({'success': True, 'data': datos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/analisis-eventos', methods=['GET'])
def analisis_eventos():
    """Análisis de pedidos por tipo de evento"""
    try:
        # Total eventos vs individuales
        total_pedidos = Pedido.query.count()
        pedidos_eventos = Pedido.query.filter(Pedido.es_evento == True).count()
        pedidos_individuales = total_pedidos - pedidos_eventos
        
        # Distribución por tipo de evento
        tipos_evento = db.session.query(
            Pedido.tipo_evento,
            func.count(Pedido.id).label('cantidad'),
            func.sum(Pedido.precio_ramo + Pedido.precio_envio).label('ventas')
        ).filter(
            Pedido.es_evento == True,
            Pedido.tipo_evento.isnot(None)
        ).group_by(Pedido.tipo_evento).all()
        
        datos_tipos = [{
            'tipo': row.tipo_evento,
            'cantidad': row.cantidad,
            'ventas': float(row.ventas) if row.ventas else 0
        } for row in tipos_evento]
        
        return jsonify({
            'success': True,
            'data': {
                'total_pedidos': total_pedidos,
                'pedidos_eventos': pedidos_eventos,
                'pedidos_individuales': pedidos_individuales,
                'porcentaje_eventos': (pedidos_eventos / total_pedidos * 100) if total_pedidos > 0 else 0,
                'tipos_evento': datos_tipos
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/analisis-cobranza', methods=['GET'])
def analisis_cobranza():
    """Análisis del estado de cobranza"""
    try:
        resultado = db.session.query(
            Pedido.estado_pago,
            func.count(Pedido.id).label('cantidad'),
            func.sum(Pedido.precio_ramo + Pedido.precio_envio).label('monto')
        ).group_by(Pedido.estado_pago).all()
        
        datos = [{
            'estado': row.estado_pago or 'Sin especificar',
            'cantidad': row.cantidad,
            'monto': float(row.monto) if row.monto else 0
        } for row in resultado]
        
        return jsonify({'success': True, 'data': datos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/personalizaciones', methods=['GET'])
def personalizaciones_frecuentes():
    """Análisis de personalizaciones más frecuentes"""
    try:
        # Obtener pedidos que son personalizaciones
        resultado = db.session.query(
            Pedido.tipo_personalizacion,
            func.count(Pedido.id).label('cantidad')
        ).filter(
            Pedido.tipo_personalizacion.isnot(None)
        ).group_by(Pedido.tipo_personalizacion).order_by(
            func.count(Pedido.id).desc()
        ).all()
        
        datos = [{
            'tipo': row.tipo_personalizacion,
            'cantidad': row.cantidad
        } for row in resultado]
        
        return jsonify({'success': True, 'data': datos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/ventas-dia-semana', methods=['GET'])
def ventas_dia_semana():
    """Ventas por día de la semana (por fecha de entrega)"""
    try:
        # Obtener parámetros de año y mes (por defecto: mes actual)
        año = request.args.get('año', datetime.now().year, type=int)
        mes = request.args.get('mes', datetime.now().month, type=int)
        
        # Calcular primer y último día del mes
        primer_dia = datetime(año, mes, 1)
        if mes == 12:
            ultimo_dia = datetime(año + 1, 1, 1)
        else:
            ultimo_dia = datetime(año, mes + 1, 1)
        
        # SQLite usa números 0-6 para días (0=Domingo)
        resultado = db.session.query(
            func.strftime('%w', Pedido.fecha_entrega).label('dia'),
            func.count(Pedido.id).label('cantidad'),
            func.sum(Pedido.precio_ramo + Pedido.precio_envio).label('ventas')
        ).filter(
            Pedido.fecha_entrega >= primer_dia,
            Pedido.fecha_entrega < ultimo_dia,
            Pedido.fecha_entrega.isnot(None)
        ).group_by('dia').order_by('dia').all()
        
        # Crear diccionario con todos los días inicializados en 0
        dias_nombres = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']
        datos_dict = {i: {'dia': nombre, 'cantidad': 0, 'ventas': 0.0} for i, nombre in enumerate(dias_nombres)}
        
        # Llenar con los datos reales
        for row in resultado:
            dia_num = int(row.dia)
            datos_dict[dia_num] = {
                'dia': dias_nombres[dia_num],
                'cantidad': row.cantidad,
                'ventas': float(row.ventas) if row.ventas else 0
            }
        
        # Convertir a lista ordenada (Lunes primero)
        # Reordenar: [1,2,3,4,5,6,0] para que Lunes sea primero
        datos = [datos_dict[i] for i in [1, 2, 3, 4, 5, 6, 0]]
        
        return jsonify({
            'success': True, 
            'data': datos,
            'mes': mes,
            'año': año
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/canales-venta', methods=['GET'])
def canales_venta():
    """Rendimiento por canal de venta"""
    try:
        resultado = db.session.query(
            Pedido.canal,
            func.count(Pedido.id).label('cantidad'),
            func.sum(Pedido.precio_ramo + Pedido.precio_envio).label('ventas')
        ).filter(
            Pedido.canal.isnot(None)
        ).group_by(Pedido.canal).all()
        
        datos = [{
            'canal': row.canal,
            'cantidad': row.cantidad,
            'ventas': float(row.ventas) if row.ventas else 0
        } for row in resultado]
        
        return jsonify({'success': True, 'data': datos})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/arreglos-por-motivo', methods=['GET'])
def arreglos_por_motivo():
    """Análisis de arreglos más solicitados por cada motivo (TODOS los pedidos)"""
    try:
        from collections import Counter, defaultdict
        
        anio = request.args.get('anio', type=int)
        mes = request.args.get('mes', type=int)
        
        # Construir query base para TODOS los pedidos
        query = Pedido.query.filter(
            Pedido.estado != 'Cancelado'
        )
        
        # Aplicar filtros si se especifican
        if anio and mes:
            primer_dia = datetime(anio, mes, 1)
            if mes == 12:
                ultimo_dia = datetime(anio + 1, 1, 1)
            else:
                ultimo_dia = datetime(anio, mes + 1, 1)
            
            query = query.filter(
                Pedido.fecha_pedido >= primer_dia,
                Pedido.fecha_pedido < ultimo_dia
            )
        
        pedidos = query.all()
        
        # Contadores
        motivos_counter = Counter()
        motivos_arreglos = defaultdict(Counter)
        
        # Procesar cada pedido
        for p in pedidos:
            if p.motivo and p.arreglo_pedido:
                motivo = p.motivo.strip().title()
                arreglo = p.arreglo_pedido.strip()
                
                motivos_counter[motivo] += 1
                motivos_arreglos[motivo][arreglo] += 1
        
        # Preparar datos de arreglos por motivo
        motivos_con_arreglos = []
        for motivo, cantidad in motivos_counter.most_common(15):
            arreglos_del_motivo = [
                {'nombre': arreglo, 'cantidad': cant}
                for arreglo, cant in motivos_arreglos[motivo].most_common(10)
            ]
            motivos_con_arreglos.append({
                'motivo': motivo,
                'total_pedidos': cantidad,
                'arreglos': arreglos_del_motivo
            })
        
        return jsonify({
            'success': True,
            'data': motivos_con_arreglos,
            'total_motivos': len(motivos_counter),
            'total_pedidos': len(pedidos),
            'mes': mes,
            'anio': anio
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/anticipacion-pedidos', methods=['GET'])
def anticipacion_pedidos():
    """Análisis de días de anticipación entre pedido y entrega, por canal"""
    try:
        from collections import defaultdict
        from datetime import timedelta
        
        anio = request.args.get('anio', type=int)
        mes = request.args.get('mes', type=int)
        
        # Construir query base
        query = Pedido.query.filter(
            Pedido.estado != 'Cancelado',
            Pedido.fecha_pedido.isnot(None),
            Pedido.fecha_entrega.isnot(None)
        )
        
        # Aplicar filtros si se especifican
        if anio and mes:
            primer_dia = datetime(anio, mes, 1)
            if mes == 12:
                ultimo_dia = datetime(anio + 1, 1, 1)
            else:
                ultimo_dia = datetime(anio, mes + 1, 1)
            
            query = query.filter(
                Pedido.fecha_pedido >= primer_dia,
                Pedido.fecha_pedido < ultimo_dia
            )
        
        pedidos = query.all()
        
        # Categorías de anticipación
        def categorizar_anticipacion(dias):
            if dias == 0:
                return "Mismo día"
            elif dias == 1:
                return "1 día"
            elif dias >= 2 and dias <= 3:
                return "2-3 días"
            elif dias >= 4 and dias <= 7:
                return "4-7 días"
            elif dias >= 8 and dias <= 14:
                return "8-14 días"
            elif dias >= 15 and dias <= 30:
                return "15-30 días"
            else:
                return "Más de 30 días"
        
        # Estructura: {canal: {categoria: cantidad}}
        anticipacion_por_canal = defaultdict(lambda: defaultdict(int))
        total_por_categoria = defaultdict(int)
        promedio_dias_por_canal = defaultdict(list)
        
        # Procesar cada pedido
        for p in pedidos:
            try:
                # Calcular días de anticipación
                dias = (p.fecha_entrega - p.fecha_pedido).days
                
                # Solo considerar anticipaciones positivas (no negativas)
                if dias >= 0:
                    canal = p.canal if p.canal else "Sin canal"
                    categoria = categorizar_anticipacion(dias)
                    
                    anticipacion_por_canal[canal][categoria] += 1
                    total_por_categoria[categoria] += 1
                    promedio_dias_por_canal[canal].append(dias)
            except:
                continue
        
        # Preparar datos por canal
        datos_por_canal = []
        for canal, categorias in anticipacion_por_canal.items():
            dias_promedio = sum(promedio_dias_por_canal[canal]) / len(promedio_dias_por_canal[canal]) if promedio_dias_por_canal[canal] else 0
            
            categorias_data = [
                {'categoria': cat, 'cantidad': cant}
                for cat, cant in sorted(categorias.items(), key=lambda x: x[1], reverse=True)
            ]
            
            datos_por_canal.append({
                'canal': canal,
                'categorias': categorias_data,
                'total_pedidos': sum(categorias.values()),
                'promedio_dias': round(dias_promedio, 1)
            })
        
        # Ordenar por total de pedidos
        datos_por_canal.sort(key=lambda x: x['total_pedidos'], reverse=True)
        
        # Datos generales (todos los canales)
        categorias_generales = [
            {'categoria': cat, 'cantidad': cant}
            for cat, cant in sorted(total_por_categoria.items(), key=lambda x: x[1], reverse=True)
        ]
        
        # Calcular promedio general
        todos_dias = [d for dias_list in promedio_dias_por_canal.values() for d in dias_list]
        promedio_general = sum(todos_dias) / len(todos_dias) if todos_dias else 0
        
        return jsonify({
            'success': True,
            'data': {
                'por_canal': datos_por_canal,
                'general': categorias_generales,
                'promedio_general': round(promedio_general, 1),
                'total_pedidos': len(pedidos)
            },
            'mes': mes,
            'anio': anio
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/colores-frecuentes', methods=['GET'])
def colores_frecuentes():
    """Análisis de colores más frecuentes en TODOS los pedidos"""
    try:
        import json as json_lib
        from collections import Counter
        
        anio = request.args.get('anio', type=int)
        mes = request.args.get('mes', type=int)
        
        # Función para normalizar colores
        def normalizar_color(color):
            if not color:
                return None
            
            color_lower = color.lower().strip()
            
            # Diccionario de normalización
            normalizaciones = {
                'blanco': 'Blanco', 'blanca': 'Blanco', 'blancos': 'Blanco', 'blancas': 'Blanco',
                'rojo': 'Rojo', 'roja': 'Rojo', 'rojos': 'Rojo', 'rojas': 'Rojo',
                'rosado': 'Rosado', 'rosada': 'Rosado', 'rosados': 'Rosado', 'rosadas': 'Rosado',
                'rosa': 'Rosa', 'rosas': 'Rosa',
                'amarillo': 'Amarillo', 'amarilla': 'Amarillo', 'amarillos': 'Amarillo', 'amarillas': 'Amarillo',
                'azul': 'Azul', 'azules': 'Azul',
                'verde': 'Verde', 'verdes': 'Verde',
                'naranjo': 'Naranjo', 'naranja': 'Naranjo', 'naranjos': 'Naranjo', 'naranjas': 'Naranjo',
                'morado': 'Morado', 'morada': 'Morado', 'morados': 'Morado', 'moradas': 'Morado',
                'fucsia': 'Fucsia', 'fucsias': 'Fucsia',
                'colorido': 'Colorido', 'colorida': 'Colorido', 'coloridos': 'Colorido', 'coloridas': 'Colorido',
                'lila': 'Lila', 'lilas': 'Lila',
                'celeste': 'Celeste', 'celestes': 'Celeste',
                'café': 'Café', 'cafés': 'Café', 'cafe': 'Café',
                'beige': 'Beige',
                'negro': 'Negro', 'negra': 'Negro', 'negros': 'Negro', 'negras': 'Negro',
                'gris': 'Gris', 'grises': 'Gris',
                'turquesa': 'Turquesa', 'turquesas': 'Turquesa',
                'durazno': 'Durazno', 'duraznos': 'Durazno',
                'salmón': 'Salmón', 'salmon': 'Salmón',
                'burdeo': 'Burdeo', 'burgundy': 'Burdeo',
                'lavanda': 'Lavanda',
                'coral': 'Coral',
                'crema': 'Crema',
                'pastel': 'Pastel', 'pasteles': 'Pastel'
            }
            
            return normalizaciones.get(color_lower, color.title())
        
        # Construir query base
        query = Pedido.query.filter(
            Pedido.estado != 'Cancelado'
        )
        
        # Aplicar filtros si se especifican
        if anio and mes:
            primer_dia = datetime(anio, mes, 1)
            if mes == 12:
                ultimo_dia = datetime(anio + 1, 1, 1)
            else:
                ultimo_dia = datetime(anio, mes + 1, 1)
            
            query = query.filter(
                Pedido.fecha_pedido >= primer_dia,
                Pedido.fecha_pedido < ultimo_dia
            )
        
        pedidos = query.all()
        
        # Contador de colores
        colores_counter = Counter()
        
        # Procesar cada pedido
        for p in pedidos:
            # Intentar obtener colores de colores_solicitados (JSON)
            if p.colores_solicitados:
                try:
                    colores = json_lib.loads(p.colores_solicitados)
                    if isinstance(colores, list):
                        for color in colores:
                            color_norm = normalizar_color(color)
                            if color_norm:
                                colores_counter[color_norm] += 1
                except (json_lib.JSONDecodeError, TypeError):
                    # Si no es JSON, intentar parsear como string
                    for color in str(p.colores_solicitados).split(','):
                        color_norm = normalizar_color(color)
                        if color_norm:
                            colores_counter[color_norm] += 1
        
        # Preparar datos para respuesta (top 20)
        colores_data = [
            {'color': color, 'cantidad': cantidad}
            for color, cantidad in colores_counter.most_common(20)
        ]
        
        return jsonify({
            'success': True,
            'data': colores_data,
            'total_pedidos': len(pedidos),
            'total_colores_unicos': len(colores_counter),
            'mes': mes,
            'anio': anio
        })
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e)}), 500

@bp.route('/analisis-personalizaciones', methods=['GET'])
def analisis_personalizaciones():
    """Análisis completo de personalizaciones (filtrable por mes y año)"""
    try:
        import json as json_lib
        from collections import Counter, defaultdict
        
        anio = request.args.get('anio', type=int)
        mes = request.args.get('mes', type=int)
        
        # Construir query base para personalizaciones
        query = Pedido.query.filter(
            Pedido.arreglo_pedido == 'Personalización'
        )
        
        # Aplicar filtros si se especifican
        if anio and mes:
            primer_dia = datetime(anio, mes, 1)
            if mes == 12:
                ultimo_dia = datetime(anio + 1, 1, 1)
            else:
                ultimo_dia = datetime(anio, mes + 1, 1)
            
            query = query.filter(
                Pedido.fecha_pedido >= primer_dia,
                Pedido.fecha_pedido < ultimo_dia
            )
        
        personalizaciones = query.all()
        
        # Contadores
        colores_counter = Counter()
        tipos_counter = Counter()
        motivos_counter = Counter()
        motivos_arreglos = defaultdict(Counter)  # Nuevo: arreglos por motivo
        
        total_personalizaciones = len(personalizaciones)
        ventas_totales = sum(p.precio_ramo or 0 for p in personalizaciones)
        
        # Procesar cada personalización
        for p in personalizaciones:
            # Colores
            if p.colores_solicitados:
                try:
                    colores = json_lib.loads(p.colores_solicitados)
                    if isinstance(colores, list):
                        for color in colores:
                            if color and color.strip():
                                colores_counter[color.strip().title()] += 1
                except (json_lib.JSONDecodeError, TypeError):
                    # Si no es JSON, intentar parsear como string simple
                    if p.colores_solicitados:
                        for color in p.colores_solicitados.split(','):
                            color = color.strip().title()
                            if color:
                                colores_counter[color] += 1
            
            # Tipos de personalización
            if p.tipo_personalizacion:
                tipo = p.tipo_personalizacion.strip().title()
                tipos_counter[tipo] += 1
                
                # Nuevo: Asociar tipo de arreglo con motivo
                if p.motivo:
                    motivo = p.motivo.strip().title()
                    motivos_arreglos[motivo][tipo] += 1
            
            # Motivos
            if p.motivo:
                motivos_counter[p.motivo.strip().title()] += 1
        
        # Preparar datos para respuesta
        colores_data = [
            {'color': color, 'cantidad': cantidad}
            for color, cantidad in colores_counter.most_common(15)
        ]
        
        tipos_data = [
            {'tipo': tipo, 'cantidad': cantidad}
            for tipo, cantidad in tipos_counter.most_common(10)
        ]
        
        motivos_data = [
            {'motivo': motivo, 'cantidad': cantidad}
            for motivo, cantidad in motivos_counter.most_common(10)
        ]
        
        # Nuevo: Preparar datos de arreglos por motivo
        motivos_con_arreglos = []
        for motivo, cantidad in motivos_counter.most_common(10):
            arreglos_del_motivo = [
                {'tipo': tipo, 'cantidad': cant}
                for tipo, cant in motivos_arreglos[motivo].most_common(5)
            ]
            motivos_con_arreglos.append({
                'motivo': motivo,
                'cantidad': cantidad,
                'arreglos': arreglos_del_motivo
            })
        
        return jsonify({
            'success': True,
            'data': {
                'total_personalizaciones': total_personalizaciones,
                'ventas_totales': float(ventas_totales),
                'ticket_promedio': float(ventas_totales / total_personalizaciones) if total_personalizaciones > 0 else 0,
                'colores': colores_data,
                'tipos': tipos_data,
                'motivos': motivos_data,
                'motivos_con_arreglos': motivos_con_arreglos  # Nuevo
            },
            'mes': mes,
            'anio': anio
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

