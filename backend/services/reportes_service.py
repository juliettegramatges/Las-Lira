"""
Servicio de reportes y análisis
Contiene toda la lógica de negocio para generar reportes, KPIs y análisis
"""

from extensions import db
from models.pedido import Pedido
from models.cliente import Cliente
from models.producto import Producto
from datetime import datetime, timedelta
from sqlalchemy import func, extract, case
import re


class ReportesService:
    """Servicio para generación de reportes y análisis de negocio"""

    @staticmethod
    def _title_case_keep_acronyms(text):
        """Mantiene acrónimos en mayúsculas mientras capitaliza otras palabras"""
        if not text:
            return text
        parts = [w.upper() if w.isupper() and len(w) <= 4 else w.capitalize() for w in text.split(' ')]
        return ' '.join(parts)

    @staticmethod
    def normalizar_nombre_arreglo(nombre):
        """
        Normaliza nombres de arreglo eliminando prefijo genérico 'Arreglo Floral'

        Args:
            nombre: nombre del arreglo a normalizar

        Returns:
            str: nombre normalizado o None si es genérico
        """
        if not nombre:
            return None

        texto = nombre.strip()

        # Si comienza con "Arreglo " pero NO con "Arreglo Floral", conservar el nombre completo
        if re.match(r"(?i)^\s*arreglo\s+(?!floral\b).+", texto):
            texto = re.sub(r"\s+", " ", texto).strip()
            return ReportesService._title_case_keep_acronyms(texto)

        patron = re.compile(r"(?i)^\s*arreglo\s*floral\s*(?:[-:–—·]*\s*)?(?P<tipo>.+?)\s*$")
        m = patron.match(texto)

        if m:
            candidato = m.group('tipo').strip()
        else:
            m2 = re.search(r"(?i)arreglo\s*floral\s*(?:[-:–—·]*\s*)?(?P<tipo>.+)$", texto)
            candidato = m2.group('tipo').strip() if m2 else texto

        # Limpiar prefijos como 'tipo de'
        candidato = re.sub(r"(?i)^(tipo\s*(de)?\s*|de\s+)", "", candidato).strip()
        candidato = re.sub(r"\s+", " ", candidato)

        # Excluir si quedó genérico o vacío
        if not candidato or candidato.lower() in ("arreglo floral", "arreglo", "floral"):
            return None

        # Excluir si es un motivo estándar
        try:
            from config.motivos import obtener_motivos
            motivos = set(m.lower() for m in obtener_motivos())
            if candidato.lower() in motivos:
                return None
        except Exception:
            pass

        return ReportesService._title_case_keep_acronyms(candidato)

    @staticmethod
    def obtener_kpis():
        """
        Obtiene KPIs principales del dashboard

        Returns:
            dict: KPIs del mes actual vs mes anterior
        """
        hoy = datetime.now()
        primer_dia_mes = hoy.replace(day=1)
        mes_anterior = (primer_dia_mes - timedelta(days=1)).replace(day=1)

        # Ventas del mes actual
        ventas_mes = db.session.query(
            func.sum(Pedido.precio_ramo + Pedido.precio_envio)
        ).filter(
            Pedido.fecha_pedido >= primer_dia_mes,
            Pedido.estado != 'Cancelado'
        ).scalar() or 0

        # Ventas del mes anterior
        ventas_mes_anterior = db.session.query(
            func.sum(Pedido.precio_ramo + Pedido.precio_envio)
        ).filter(
            Pedido.fecha_pedido >= mes_anterior,
            Pedido.fecha_pedido < primer_dia_mes,
            Pedido.estado != 'Cancelado'
        ).scalar() or 0

        # Pedidos del mes
        pedidos_mes = Pedido.query.filter(
            Pedido.fecha_pedido >= primer_dia_mes,
            Pedido.estado != 'Cancelado'
        ).count()

        # Pedidos mes anterior
        pedidos_mes_anterior = Pedido.query.filter(
            Pedido.fecha_pedido >= mes_anterior,
            Pedido.fecha_pedido < primer_dia_mes,
            Pedido.estado != 'Cancelado'
        ).count()

        # Ticket promedio
        ticket_promedio = ventas_mes / pedidos_mes if pedidos_mes > 0 else 0

        # Crecimiento ventas
        crecimiento_ventas = ((ventas_mes - ventas_mes_anterior) / ventas_mes_anterior * 100) if ventas_mes_anterior > 0 else 0

        # Crecimiento pedidos
        crecimiento_pedidos = ((pedidos_mes - pedidos_mes_anterior) / pedidos_mes_anterior * 100) if pedidos_mes_anterior > 0 else 0

        # Clientes nuevos este mes
        clientes_nuevos_mes = Cliente.query.filter(
            Cliente.fecha_registro >= primer_dia_mes
        ).count()

        # Clientes nuevos mes anterior
        clientes_nuevos_mes_anterior = Cliente.query.filter(
            Cliente.fecha_registro >= mes_anterior,
            Cliente.fecha_registro < primer_dia_mes
        ).count()

        # Crecimiento clientes
        crecimiento_clientes = ((clientes_nuevos_mes - clientes_nuevos_mes_anterior) / clientes_nuevos_mes_anterior * 100) if clientes_nuevos_mes_anterior > 0 else 0

        # Tasa de entrega a tiempo
        entregados_a_tiempo = Pedido.query.filter(
            Pedido.fecha_pedido >= primer_dia_mes,
            Pedido.estado == 'Despachados',
            Pedido.fecha_entrega >= datetime.now().date()
        ).count()

        total_despachados = Pedido.query.filter(
            Pedido.fecha_pedido >= primer_dia_mes,
            Pedido.estado == 'Despachados'
        ).count()

        tasa_entrega = (entregados_a_tiempo / total_despachados * 100) if total_despachados > 0 else 0

        return {
            'ventas_mes': float(ventas_mes),
            'ventas_mes_anterior': float(ventas_mes_anterior),
            'pedidos_mes': pedidos_mes,
            'pedidos_mes_anterior': pedidos_mes_anterior,
            'ticket_promedio': float(ticket_promedio),
            'crecimiento_ventas': float(crecimiento_ventas),
            'crecimiento_pedidos': float(crecimiento_pedidos),
            'clientes_nuevos_mes': clientes_nuevos_mes,
            'clientes_nuevos_mes_anterior': clientes_nuevos_mes_anterior,
            'crecimiento_clientes': float(crecimiento_clientes),
            'tasa_entrega': float(tasa_entrega)
        }

    @staticmethod
    def obtener_ventas_mensuales(meses=12):
        """
        Obtiene ventas agrupadas por mes (últimos N meses)

        Args:
            meses: cantidad de meses a retornar (default: 12)

        Returns:
            list: ventas por mes con formato {mes, ventas, nombre}
        """
        from datetime import datetime, timedelta
        
        # Calcular fecha límite (últimos N meses)
        fecha_limite = datetime.now() - timedelta(days=meses * 30)
        
        ventas = db.session.query(
            extract('year', Pedido.fecha_pedido).label('año'),
            extract('month', Pedido.fecha_pedido).label('mes'),
            func.sum(Pedido.precio_ramo + Pedido.precio_envio).label('total')
        ).filter(
            Pedido.fecha_pedido >= fecha_limite,
            Pedido.estado != 'Cancelado'
        ).group_by('año', 'mes').order_by('año', 'mes').all()

        # Mapear nombres de meses
        nombres_meses = {
            1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
            7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
        }

        return [
            {
                'mes': int(v.mes),
                'ventas': float(v.total or 0),
                'nombre': f"{nombres_meses.get(int(v.mes), int(v.mes))}/{int(v.año) % 100}"
            }
            for v in ventas
        ]

    @staticmethod
    def obtener_top_productos(limite=10, anio=None, mes=None):
        """
        Obtiene los productos más vendidos

        Args:
            limite: cantidad de productos a retornar
            anio: año para filtrar (opcional)
            mes: mes para filtrar (opcional)

        Returns:
            list: productos ordenados por cantidad vendida
        """
        query = db.session.query(
            Pedido.arreglo_pedido,
            func.count(Pedido.id).label('cantidad'),
            func.sum(Pedido.precio_ramo).label('ventas')
        ).filter(
            Pedido.arreglo_pedido.isnot(None),
            Pedido.estado != 'Cancelado'
        )

        # Aplicar filtros de fecha si se proporcionan
        if anio and mes:
            query = query.filter(
                extract('year', Pedido.fecha_pedido) == anio,
                extract('month', Pedido.fecha_pedido) == mes
            )
        elif anio:
            query = query.filter(extract('year', Pedido.fecha_pedido) == anio)

        productos = query.group_by(
            Pedido.arreglo_pedido
        ).order_by(
            func.count(Pedido.id).desc()
        ).limit(limite).all()

        return [
            {
                'producto': p.arreglo_pedido,
                'cantidad': p.cantidad,
                'ventas': float(p.ventas or 0)
            }
            for p in productos
        ]

    @staticmethod
    def obtener_distribucion_tipos():
        """
        Obtiene la distribución de pedidos por tipo

        Returns:
            list: distribución por tipo
        """
        tipos = db.session.query(
            Pedido.tipo_pedido,
            func.count(Pedido.id).label('cantidad')
        ).filter(
            Pedido.tipo_pedido.isnot(None)
        ).group_by(
            Pedido.tipo_pedido
        ).all()

        return [
            {
                'tipo': t.tipo_pedido,
                'cantidad': t.cantidad
            }
            for t in tipos
        ]

    @staticmethod
    def obtener_top_clientes(limite=10):
        """
        Obtiene los mejores clientes por gasto total

        Args:
            limite: cantidad de clientes a retornar

        Returns:
            list: clientes ordenados por gasto total
        """
        clientes = Cliente.query.filter(
            Cliente.total_gastado > 0
        ).order_by(
            Cliente.total_gastado.desc()
        ).limit(limite).all()

        return [
            {
                'id': c.id,
                'nombre': c.nombre,
                'total_gastado': float(c.total_gastado or 0),
                'total_pedidos': c.total_pedidos,
                'tipo_cliente': c.tipo_cliente
            }
            for c in clientes
        ]

    @staticmethod
    def obtener_distribucion_clientes():
        """
        Obtiene la distribución de clientes por tipo

        Returns:
            list: distribución por tipo de cliente
        """
        distribucion = db.session.query(
            Cliente.tipo_cliente,
            func.count(Cliente.id).label('cantidad')
        ).group_by(
            Cliente.tipo_cliente
        ).all()

        return [
            {
                'tipo': d.tipo_cliente,
                'cantidad': d.cantidad
            }
            for d in distribucion
        ]

    @staticmethod
    def obtener_comunas_frecuentes(limite=10):
        """
        Obtiene las comunas con más pedidos

        Args:
            limite: cantidad de comunas a retornar

        Returns:
            list: comunas ordenadas por frecuencia
        """
        comunas = db.session.query(
            Pedido.comuna,
            func.count(Pedido.id).label('cantidad')
        ).filter(
            Pedido.comuna.isnot(None)
        ).group_by(
            Pedido.comuna
        ).order_by(
            func.count(Pedido.id).desc()
        ).limit(limite).all()

        return [
            {
                'comuna': c.comuna,
                'cantidad': c.cantidad
            }
            for c in comunas
        ]

    @staticmethod
    def analisis_eventos():
        """
        Analiza eventos y sus estados

        Returns:
            dict: estadísticas de eventos
        """
        from models.evento import Evento

        total_eventos = Evento.query.count()

        estados = db.session.query(
            Evento.estado,
            func.count(Evento.id).label('cantidad')
        ).group_by(Evento.estado).all()

        confirmados = Evento.query.filter_by(estado='Confirmado').count()

        ingresos_eventos = db.session.query(
            func.sum(Evento.precio_propuesta)
        ).filter_by(estado='Confirmado').scalar() or 0

        return {
            'total': total_eventos,
            'confirmados': confirmados,
            'ingresos_total': float(ingresos_eventos),
            'por_estado': [
                {
                    'estado': e.estado,
                    'cantidad': e.cantidad
                }
                for e in estados
            ]
        }

    @staticmethod
    def analisis_cobranza():
        """
        Analiza el estado de cobranza de pedidos

        Returns:
            list: array de objetos con estado, cantidad y monto
        """
        # Contar y sumar pedidos pagados
        pedidos_pagados = Pedido.query.filter(
            Pedido.estado_pago == 'Pagado',
            Pedido.estado != 'Cancelado'
        ).all()
        cantidad_pagados = len(pedidos_pagados)
        monto_pagado = sum(float((p.precio_ramo or 0) + (p.precio_envio or 0)) for p in pedidos_pagados)

        # Contar y sumar pedidos pendientes
        pedidos_pendientes = Pedido.query.filter(
            Pedido.estado_pago != 'Pagado',
            Pedido.estado != 'Cancelado'
        ).all()
        cantidad_pendientes = len(pedidos_pendientes)
        monto_pendiente = sum(float((p.precio_ramo or 0) + (p.precio_envio or 0)) for p in pedidos_pendientes)

        # Contar y sumar pedidos vencidos
        from datetime import datetime
        hoy = datetime.now()
        pedidos_vencidos = Pedido.query.filter(
            Pedido.estado_pago != 'Pagado',
            Pedido.fecha_maxima_pago < hoy,
            Pedido.estado != 'Cancelado'
        ).all()
        cantidad_vencidos = len(pedidos_vencidos)
        monto_vencido = sum(float((p.precio_ramo or 0) + (p.precio_envio or 0)) for p in pedidos_vencidos)

        return [
            {
                'estado': 'Pagado',
                'cantidad': cantidad_pagados,
                'monto': monto_pagado
            },
            {
                'estado': 'Pendiente',
                'cantidad': cantidad_pendientes,
                'monto': monto_pendiente
            },
            {
                'estado': 'Vencido',
                'cantidad': cantidad_vencidos,
                'monto': monto_vencido
            }
        ]

    @staticmethod
    def obtener_personalizaciones():
        """
        Obtiene resumen de personalizaciones de pedidos

        Returns:
            list: personalizaciones más frecuentes
        """
        personalizaciones = db.session.query(
            Pedido.tipo_personalizacion,
            func.count(Pedido.id).label('cantidad')
        ).filter(
            Pedido.tipo_personalizacion.isnot(None)
        ).group_by(
            Pedido.tipo_personalizacion
        ).order_by(
            func.count(Pedido.id).desc()
        ).all()

        return [
            {
                'tipo': p.tipo_personalizacion,
                'cantidad': p.cantidad
            }
            for p in personalizaciones
        ]

    @staticmethod
    def ventas_por_dia_semana(anio=None, mes=None):
        """
        Analiza ventas agrupadas por día de la semana

        Args:
            anio: año para filtrar (opcional)
            mes: mes para filtrar (opcional)

        Returns:
            list: ventas por día de la semana
        """
        # SQLite usa strftime para obtener el día de la semana
        query = db.session.query(
            func.strftime('%w', Pedido.fecha_entrega).label('dia_semana'),
            func.count(Pedido.id).label('cantidad'),
            func.sum(Pedido.precio_ramo + Pedido.precio_envio).label('ventas')
        ).filter(
            Pedido.fecha_entrega.isnot(None),
            Pedido.estado != 'Cancelado'
        )

        # Aplicar filtros de fecha
        if anio and mes:
            query = query.filter(
                extract('year', Pedido.fecha_entrega) == anio,
                extract('month', Pedido.fecha_entrega) == mes
            )
        elif anio:
            query = query.filter(extract('year', Pedido.fecha_entrega) == anio)

        ventas = query.group_by('dia_semana').all()

        dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']

        return [
            {
                'dia': dias[int(v.dia_semana)],
                'cantidad': v.cantidad,
                'ventas': float(v.ventas or 0)
            }
            for v in ventas
        ]

    @staticmethod
    def obtener_canales_venta():
        """
        Obtiene distribución de ventas por canal

        Returns:
            list: ventas por canal
        """
        canales = db.session.query(
            Pedido.canal,
            func.count(Pedido.id).label('cantidad'),
            func.sum(Pedido.precio_ramo + Pedido.precio_envio).label('total')
        ).group_by(Pedido.canal).all()

        return [
            {
                'canal': c.canal,
                'cantidad': c.cantidad,
                'total': float(c.total or 0)
            }
            for c in canales
        ]

    @staticmethod
    def arreglos_por_motivo(anio=None, mes=None):
        """
        Obtiene los arreglos más solicitados por cada motivo

        Args:
            anio: año para filtrar (opcional)
            mes: mes para filtrar (opcional)

        Returns:
            dict: arreglos agrupados por motivo
        """
        query = Pedido.query.filter(
            Pedido.motivo.isnot(None),
            Pedido.arreglo_pedido.isnot(None),
            Pedido.estado != 'Cancelado'
        )

        # Aplicar filtros de fecha
        if anio and mes:
            query = query.filter(
                extract('year', Pedido.fecha_pedido) == anio,
                extract('month', Pedido.fecha_pedido) == mes
            )
        elif anio:
            query = query.filter(extract('year', Pedido.fecha_pedido) == anio)

        pedidos = query.all()

        # Agrupar por motivo
        por_motivo = {}
        for pedido in pedidos:
            motivo = pedido.motivo
            arreglo = ReportesService.normalizar_nombre_arreglo(pedido.arreglo_pedido)

            if not arreglo:
                continue

            if motivo not in por_motivo:
                por_motivo[motivo] = {}

            if arreglo not in por_motivo[motivo]:
                por_motivo[motivo][arreglo] = 0

            por_motivo[motivo][arreglo] += 1

        # Convertir a lista ordenada
        resultado = []
        for motivo, arreglos in por_motivo.items():
            total_pedidos = sum(arreglos.values())
            arreglos_ordenados = sorted(
                [{'nombre': nombre, 'cantidad': cantidad} for nombre, cantidad in arreglos.items()],
                key=lambda x: x['cantidad'],
                reverse=True
            )[:5]  # Top 5 por motivo

            resultado.append({
                'motivo': motivo,
                'total_pedidos': total_pedidos,
                'arreglos': arreglos_ordenados
            })

        # Ordenar por total de pedidos descendente
        resultado.sort(key=lambda x: x['total_pedidos'], reverse=True)

        return resultado

    @staticmethod
    def analisis_anticipacion_pedidos(anio=None, mes=None):
        """
        Analiza con cuánta anticipación se hacen los pedidos

        Args:
            anio: año para filtrar (opcional)
            mes: mes para filtrar (opcional)

        Returns:
            dict: estadísticas de anticipación por canal
        """
        query = Pedido.query.filter(
            Pedido.fecha_pedido.isnot(None),
            Pedido.fecha_entrega.isnot(None),
            Pedido.estado != 'Cancelado'
        )

        # Aplicar filtros de fecha
        if anio and mes:
            query = query.filter(
                extract('year', Pedido.fecha_pedido) == anio,
                extract('month', Pedido.fecha_pedido) == mes
            )
        elif anio:
            query = query.filter(extract('year', Pedido.fecha_pedido) == anio)

        pedidos = query.all()

        if not pedidos:
            return {
                'total_pedidos': 0,
                'promedio_general': 0,
                'general': [],
                'por_canal': []
            }

        # Análisis general
        diferencias_general = []
        rangos_general = {'mismo_dia': 0, '1_3_dias': 0, '4_7_dias': 0, 'mas_7_dias': 0}

        # Análisis por canal
        por_canal = {}

        for pedido in pedidos:
            dias = (pedido.fecha_entrega - pedido.fecha_pedido).days
            diferencias_general.append(dias)

            # Clasificar en rangos generales
            if dias == 0:
                rangos_general['mismo_dia'] += 1
            elif 1 <= dias <= 3:
                rangos_general['1_3_dias'] += 1
            elif 4 <= dias <= 7:
                rangos_general['4_7_dias'] += 1
            else:
                rangos_general['mas_7_dias'] += 1

            # Agrupar por canal
            canal = pedido.canal or 'Sin especificar'
            if canal not in por_canal:
                por_canal[canal] = {
                    'diferencias': [],
                    'rangos': {'mismo_dia': 0, '1_3_dias': 0, '4_7_dias': 0, 'mas_7_dias': 0}
                }

            por_canal[canal]['diferencias'].append(dias)

            # Clasificar en rangos por canal
            if dias == 0:
                por_canal[canal]['rangos']['mismo_dia'] += 1
            elif 1 <= dias <= 3:
                por_canal[canal]['rangos']['1_3_dias'] += 1
            elif 4 <= dias <= 7:
                por_canal[canal]['rangos']['4_7_dias'] += 1
            else:
                por_canal[canal]['rangos']['mas_7_dias'] += 1

        promedio_general = sum(diferencias_general) / len(diferencias_general)

        # Construir resultado por canal
        resultado_canales = []
        for canal, datos in por_canal.items():
            promedio_canal = sum(datos['diferencias']) / len(datos['diferencias'])
            resultado_canales.append({
                'canal': canal,
                'total_pedidos': len(datos['diferencias']),
                'promedio_dias': round(promedio_canal, 1),
                'categorias': [
                    {'categoria': 'Mismo día', 'cantidad': datos['rangos']['mismo_dia']},
                    {'categoria': '1-3 días', 'cantidad': datos['rangos']['1_3_dias']},
                    {'categoria': '4-7 días', 'cantidad': datos['rangos']['4_7_dias']},
                    {'categoria': 'Más de 7 días', 'cantidad': datos['rangos']['mas_7_dias']}
                ]
            })

        # Ordenar canales por total de pedidos
        resultado_canales.sort(key=lambda x: x['total_pedidos'], reverse=True)

        return {
            'total_pedidos': len(pedidos),
            'promedio_general': round(promedio_general, 1),
            'general': [
                {'categoria': 'Mismo día', 'cantidad': rangos_general['mismo_dia']},
                {'categoria': '1-3 días', 'cantidad': rangos_general['1_3_dias']},
                {'categoria': '4-7 días', 'cantidad': rangos_general['4_7_dias']},
                {'categoria': 'Más de 7 días', 'cantidad': rangos_general['mas_7_dias']}
            ],
            'por_canal': resultado_canales
        }

    @staticmethod
    def obtener_colores_frecuentes(anio=None, mes=None):
        """
        Obtiene los colores más solicitados en pedidos personalizados

        Args:
            anio: año para filtrar (opcional)
            mes: mes para filtrar (opcional)

        Returns:
            list: colores ordenados por frecuencia
        """
        query = Pedido.query.filter(
            Pedido.colores_solicitados.isnot(None),
            Pedido.estado != 'Cancelado'
        )

        # Aplicar filtros de fecha
        if anio and mes:
            query = query.filter(
                extract('year', Pedido.fecha_pedido) == anio,
                extract('month', Pedido.fecha_pedido) == mes
            )
        elif anio:
            query = query.filter(extract('year', Pedido.fecha_pedido) == anio)

        pedidos = query.all()

        conteo_colores = {}
        for pedido in pedidos:
            if pedido.colores_solicitados:
                colores = [c.strip().title() for c in pedido.colores_solicitados.split(',')]
                for color in colores:
                    if color:
                        conteo_colores[color] = conteo_colores.get(color, 0) + 1

        return sorted(
            [{'color': color, 'cantidad': cantidad} for color, cantidad in conteo_colores.items()],
            key=lambda x: x['cantidad'],
            reverse=True
        )

    @staticmethod
    def analisis_personalizaciones_detallado(anio=None, mes=None):
        """
        Análisis detallado de personalizaciones (colores, tipos, motivos con arreglos)

        Args:
            anio: año para filtrar (opcional)
            mes: mes para filtrar (opcional)

        Returns:
            dict: análisis completo de personalizaciones
        """
        # Query base
        query_personalizados = Pedido.query.filter(
            Pedido.tipo_personalizacion.isnot(None),
            Pedido.estado != 'Cancelado'
        )

        query_total = Pedido.query.filter(
            Pedido.estado != 'Cancelado'
        )

        # Aplicar filtros de fecha
        if anio and mes:
            query_personalizados = query_personalizados.filter(
                extract('year', Pedido.fecha_pedido) == anio,
                extract('month', Pedido.fecha_pedido) == mes
            )
            query_total = query_total.filter(
                extract('year', Pedido.fecha_pedido) == anio,
                extract('month', Pedido.fecha_pedido) == mes
            )
        elif anio:
            query_personalizados = query_personalizados.filter(
                extract('year', Pedido.fecha_pedido) == anio
            )
            query_total = query_total.filter(
                extract('year', Pedido.fecha_pedido) == anio
            )

        total_personalizaciones = query_personalizados.count()
        total_pedidos = query_total.count()

        # Calcular ventas totales de personalizaciones
        ventas_totales = db.session.query(
            func.sum(Pedido.precio_ramo + Pedido.precio_envio)
        ).filter(
            Pedido.tipo_personalizacion.isnot(None),
            Pedido.estado != 'Cancelado'
        )

        if anio and mes:
            ventas_totales = ventas_totales.filter(
                extract('year', Pedido.fecha_pedido) == anio,
                extract('month', Pedido.fecha_pedido) == mes
            )
        elif anio:
            ventas_totales = ventas_totales.filter(
                extract('year', Pedido.fecha_pedido) == anio
            )

        ventas_totales = ventas_totales.scalar() or 0

        ticket_promedio = ventas_totales / total_personalizaciones if total_personalizaciones > 0 else 0

        # Obtener análisis de colores, tipos y motivos con filtros aplicados
        colores = ReportesService.obtener_colores_frecuentes(anio, mes)[:10]

        # Tipos de personalización
        query_tipos = db.session.query(
            Pedido.tipo_personalizacion,
            func.count(Pedido.id).label('cantidad')
        ).filter(
            Pedido.tipo_personalizacion.isnot(None),
            Pedido.estado != 'Cancelado'
        )

        if anio and mes:
            query_tipos = query_tipos.filter(
                extract('year', Pedido.fecha_pedido) == anio,
                extract('month', Pedido.fecha_pedido) == mes
            )
        elif anio:
            query_tipos = query_tipos.filter(
                extract('year', Pedido.fecha_pedido) == anio
            )

        tipos = query_tipos.group_by(Pedido.tipo_personalizacion).order_by(
            func.count(Pedido.id).desc()
        ).all()

        tipos_data = [{'tipo': t.tipo_personalizacion, 'cantidad': t.cantidad} for t in tipos]

        # Motivos con cantidad
        query_motivos = db.session.query(
            Pedido.motivo,
            func.count(Pedido.id).label('cantidad')
        ).filter(
            Pedido.motivo.isnot(None),
            Pedido.tipo_personalizacion.isnot(None),
            Pedido.estado != 'Cancelado'
        )

        if anio and mes:
            query_motivos = query_motivos.filter(
                extract('year', Pedido.fecha_pedido) == anio,
                extract('month', Pedido.fecha_pedido) == mes
            )
        elif anio:
            query_motivos = query_motivos.filter(
                extract('year', Pedido.fecha_pedido) == anio
            )

        motivos = query_motivos.group_by(Pedido.motivo).order_by(
            func.count(Pedido.id).desc()
        ).all()

        motivos_data = [{'motivo': m.motivo, 'cantidad': m.cantidad} for m in motivos]

        # Obtener motivos con sus arreglos más populares
        motivos_con_arreglos = []

        query_pedidos_motivo = Pedido.query.filter(
            Pedido.motivo.isnot(None),
            Pedido.tipo_personalizacion.isnot(None),
            Pedido.arreglo_pedido.isnot(None),
            Pedido.estado != 'Cancelado'
        )

        if anio and mes:
            query_pedidos_motivo = query_pedidos_motivo.filter(
                extract('year', Pedido.fecha_pedido) == anio,
                extract('month', Pedido.fecha_pedido) == mes
            )
        elif anio:
            query_pedidos_motivo = query_pedidos_motivo.filter(
                extract('year', Pedido.fecha_pedido) == anio
            )

        pedidos_motivo = query_pedidos_motivo.all()

        # Agrupar arreglos por motivo
        por_motivo = {}
        for pedido in pedidos_motivo:
            motivo = pedido.motivo
            arreglo = pedido.tipo_personalizacion  # Usar tipo de personalización en lugar del nombre

            if motivo not in por_motivo:
                por_motivo[motivo] = {}

            if arreglo not in por_motivo[motivo]:
                por_motivo[motivo][arreglo] = 0

            por_motivo[motivo][arreglo] += 1

        # Convertir a lista con top 3 arreglos por motivo
        for motivo, arreglos in por_motivo.items():
            total = sum(arreglos.values())
            arreglos_ordenados = sorted(
                [{'tipo': tipo, 'cantidad': cant} for tipo, cant in arreglos.items()],
                key=lambda x: x['cantidad'],
                reverse=True
            )[:3]  # Top 3 por motivo

            motivos_con_arreglos.append({
                'motivo': motivo,
                'cantidad': total,
                'arreglos': arreglos_ordenados
            })

        # Ordenar por cantidad
        motivos_con_arreglos.sort(key=lambda x: x['cantidad'], reverse=True)

        return {
            'total_personalizaciones': total_personalizaciones,
            'ventas_totales': float(ventas_totales),
            'ticket_promedio': float(ticket_promedio),
            'colores': colores,
            'tipos': tipos_data,
            'motivos': motivos_data,
            'motivos_con_arreglos': motivos_con_arreglos
        }
