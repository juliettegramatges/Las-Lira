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

        # Clientes nuevos este mes
        clientes_nuevos = Cliente.query.filter(
            Cliente.fecha_creacion >= primer_dia_mes
        ).count()

        return {
            'ventas_mes': float(ventas_mes),
            'ventas_mes_anterior': float(ventas_mes_anterior),
            'pedidos_mes': pedidos_mes,
            'pedidos_mes_anterior': pedidos_mes_anterior,
            'ticket_promedio': float(ticket_promedio),
            'crecimiento': float(crecimiento),
            'clientes_nuevos': clientes_nuevos
        }

    @staticmethod
    def obtener_ventas_mensuales(meses=6):
        """
        Obtiene ventas agrupadas por mes

        Args:
            meses: cantidad de meses a retornar

        Returns:
            list: ventas por mes
        """
        ventas = db.session.query(
            extract('year', Pedido.fecha_pedido).label('año'),
            extract('month', Pedido.fecha_pedido).label('mes'),
            func.sum(Pedido.precio_ramo + Pedido.precio_envio).label('total')
        ).group_by('año', 'mes').order_by('año', 'mes').limit(meses).all()

        return [
            {
                'año': int(v.año),
                'mes': int(v.mes),
                'total': float(v.total or 0)
            }
            for v in ventas
        ]

    @staticmethod
    def obtener_top_productos(limite=10):
        """
        Obtiene los productos más vendidos

        Args:
            limite: cantidad de productos a retornar

        Returns:
            list: productos ordenados por cantidad vendida
        """
        productos = db.session.query(
            Pedido.arreglo_pedido,
            func.count(Pedido.id).label('cantidad'),
            func.sum(Pedido.precio_ramo).label('ingreso_total')
        ).filter(
            Pedido.arreglo_pedido.isnot(None),
            Pedido.estado != 'Cancelado'
        ).group_by(
            Pedido.arreglo_pedido
        ).order_by(
            func.count(Pedido.id).desc()
        ).limit(limite).all()

        return [
            {
                'nombre': p.arreglo_pedido,
                'cantidad': p.cantidad,
                'ingreso_total': float(p.ingreso_total or 0)
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
            dict: estadísticas de cobranza
        """
        total_pendiente = db.session.query(
            func.sum(Pedido.precio_ramo + Pedido.precio_envio)
        ).filter(
            Pedido.estado_pago != 'Pagado',
            Pedido.estado != 'Cancelado'
        ).scalar() or 0

        total_pagado = db.session.query(
            func.sum(Pedido.precio_ramo + Pedido.precio_envio)
        ).filter(
            Pedido.estado_pago == 'Pagado'
        ).scalar() or 0

        return {
            'total_pendiente': float(total_pendiente),
            'total_pagado': float(total_pagado),
            'tasa_cobranza': (total_pagado / (total_pagado + total_pendiente) * 100) if (total_pagado + total_pendiente) > 0 else 0
        }

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
    def ventas_por_dia_semana():
        """
        Analiza ventas agrupadas por día de la semana

        Returns:
            list: ventas por día de la semana
        """
        # SQLite usa strftime para obtener el día de la semana
        ventas = db.session.query(
            func.strftime('%w', Pedido.fecha_entrega).label('dia_semana'),
            func.count(Pedido.id).label('cantidad'),
            func.sum(Pedido.precio_ramo + Pedido.precio_envio).label('total')
        ).filter(
            Pedido.fecha_entrega.isnot(None)
        ).group_by('dia_semana').all()

        dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado']

        return [
            {
                'dia': dias[int(v.dia_semana)],
                'cantidad': v.cantidad,
                'total': float(v.total or 0)
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
    def arreglos_por_motivo():
        """
        Obtiene los arreglos más solicitados por cada motivo

        Returns:
            dict: arreglos agrupados por motivo
        """
        pedidos = Pedido.query.filter(
            Pedido.motivo.isnot(None),
            Pedido.arreglo_pedido.isnot(None),
            Pedido.estado != 'Cancelado'
        ).all()

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
            arreglos_ordenados = sorted(
                [{'nombre': nombre, 'cantidad': cantidad} for nombre, cantidad in arreglos.items()],
                key=lambda x: x['cantidad'],
                reverse=True
            )[:5]  # Top 5 por motivo

            resultado.append({
                'motivo': motivo,
                'arreglos': arreglos_ordenados
            })

        return resultado

    @staticmethod
    def analisis_anticipacion_pedidos():
        """
        Analiza con cuánta anticipación se hacen los pedidos

        Returns:
            dict: estadísticas de anticipación
        """
        pedidos = Pedido.query.filter(
            Pedido.fecha_pedido.isnot(None),
            Pedido.fecha_entrega.isnot(None)
        ).all()

        if not pedidos:
            return {
                'promedio_dias': 0,
                'distribucion': []
            }

        diferencias = []
        for pedido in pedidos:
            dias = (pedido.fecha_entrega - pedido.fecha_pedido).days
            diferencias.append(dias)

        promedio = sum(diferencias) / len(diferencias)

        # Distribuir en rangos
        rangos = {
            'mismo_dia': 0,
            '1_3_dias': 0,
            '4_7_dias': 0,
            'mas_7_dias': 0
        }

        for dias in diferencias:
            if dias == 0:
                rangos['mismo_dia'] += 1
            elif 1 <= dias <= 3:
                rangos['1_3_dias'] += 1
            elif 4 <= dias <= 7:
                rangos['4_7_dias'] += 1
            else:
                rangos['mas_7_dias'] += 1

        return {
            'promedio_dias': round(promedio, 1),
            'distribucion': [
                {'rango': 'Mismo día', 'cantidad': rangos['mismo_dia']},
                {'rango': '1-3 días', 'cantidad': rangos['1_3_dias']},
                {'rango': '4-7 días', 'cantidad': rangos['4_7_dias']},
                {'rango': 'Más de 7 días', 'cantidad': rangos['mas_7_dias']}
            ]
        }

    @staticmethod
    def obtener_colores_frecuentes():
        """
        Obtiene los colores más solicitados en pedidos personalizados

        Returns:
            list: colores ordenados por frecuencia
        """
        pedidos = Pedido.query.filter(
            Pedido.colores_solicitados.isnot(None)
        ).all()

        conteo_colores = {}
        for pedido in pedidos:
            if pedido.colores_solicitados:
                colores = [c.strip() for c in pedido.colores_solicitados.split(',')]
                for color in colores:
                    if color:
                        conteo_colores[color] = conteo_colores.get(color, 0) + 1

        return sorted(
            [{'color': color, 'cantidad': cantidad} for color, cantidad in conteo_colores.items()],
            key=lambda x: x['cantidad'],
            reverse=True
        )

    @staticmethod
    def analisis_personalizaciones_detallado():
        """
        Análisis detallado de personalizaciones (colores, tipos, etc.)

        Returns:
            dict: análisis completo de personalizaciones
        """
        total_personalizados = Pedido.query.filter(
            Pedido.tipo_personalizacion.isnot(None)
        ).count()

        total_pedidos = Pedido.query.filter(
            Pedido.estado != 'Cancelado'
        ).count()

        porcentaje = (total_personalizados / total_pedidos * 100) if total_pedidos > 0 else 0

        colores = ReportesService.obtener_colores_frecuentes()[:10]
        tipos = ReportesService.obtener_personalizaciones()

        return {
            'total_personalizados': total_personalizados,
            'porcentaje': round(porcentaje, 1),
            'colores_frecuentes': colores,
            'tipos_personalizacion': tipos
        }
