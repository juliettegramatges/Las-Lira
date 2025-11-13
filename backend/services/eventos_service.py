"""
Servicio de gestión de eventos
Contiene toda la lógica de negocio relacionada con eventos y cotizaciones
"""

from extensions import db
from models.evento import Evento, EventoInsumo, ProductoEvento
from models.inventario import Flor, Contenedor
from models.producto import Producto
from datetime import datetime


class EventosService:
    """Servicio para operaciones de negocio de eventos"""

    @staticmethod
    def listar_eventos():
        """
        Lista todos los eventos ordenados por fecha

        Returns:
            list: eventos ordenados por fecha descendente
        """
        eventos = Evento.query.order_by(Evento.fecha_evento.desc()).all()
        return eventos

    @staticmethod
    def obtener_evento(evento_id):
        """
        Obtiene un evento por ID con sus insumos

        Args:
            evento_id: ID del evento

        Returns:
            Evento: instancia del evento o None
        """
        return Evento.query.get(evento_id)

    @staticmethod
    def generar_id_evento():
        """
        Genera un nuevo ID para un evento (formato EV001, EV002, etc.)

        Returns:
            str: nuevo ID generado
        """
        ultimo_evento = Evento.query.order_by(Evento.id.desc()).first()
        if ultimo_evento and ultimo_evento.id.startswith('EV'):
            numero = int(ultimo_evento.id[2:]) + 1
        else:
            numero = 1
        return f'EV{numero:03d}'

    @staticmethod
    def crear_evento(data):
        """
        Crea un nuevo evento (Cotización)

        Args:
            data: dict con datos del evento

        Returns:
            tuple: (success, evento/error, mensaje)
        """
        try:
            nuevo_id = EventosService.generar_id_evento()

            # Parsear fecha_evento de forma segura
            fecha_evento = None
            if data.get('fecha_evento'):
                try:
                    # Intentar parsear como ISO format
                    if 'T' in data['fecha_evento']:
                        fecha_evento = datetime.fromisoformat(data['fecha_evento'].replace('Z', '+00:00'))
                    else:
                        # Si es solo fecha (YYYY-MM-DD), agregar hora
                        fecha_evento = datetime.fromisoformat(data['fecha_evento'] + 'T00:00:00')
                except (ValueError, TypeError) as e:
                    # Si falla, intentar otros formatos comunes
                    try:
                        from dateutil import parser
                        fecha_evento = parser.parse(data['fecha_evento'])
                    except:
                        fecha_evento = None

            nuevo_evento = Evento(
                id=nuevo_id,
                cliente_nombre=data.get('cliente_nombre') or '',
                cliente_telefono=data.get('cliente_telefono') or '',
                cliente_email=data.get('cliente_email') or '',
                nombre_evento=data.get('nombre_evento') or '',
                tipo_evento=data.get('tipo_evento') or 'Boda',
                fecha_evento=fecha_evento,
                hora_evento=data.get('hora_evento') or '',
                lugar_evento=data.get('lugar_evento') or '',
                cantidad_personas=data.get('cantidad_personas', 0) or 0,
                estado='Cotización',
                margen_porcentaje=data.get('margen_porcentaje', 30) or 30,
                costo_total=data.get('costo_total', 0) or 0,
                precio_propuesta=data.get('precio_propuesta', 0) or 0,
                notas_cotizacion=data.get('notas_cotizacion') or ''
            )

            db.session.add(nuevo_evento)
            db.session.flush()  # Para que el evento tenga ID antes de agregar insumos
            
            # No recalcular costos aquí porque aún no hay insumos
            # Se recalculará después de agregar todos los insumos
            
            db.session.commit()

            return True, nuevo_evento, 'Evento creado exitosamente'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def recalcular_costos_evento(evento):
        """
        Recalcula los costos totales y precios del evento

        Args:
            evento: instancia del Evento

        Returns:
            None (modifica el evento in-place)
        """
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
        evento.precio_propuesta = evento.costo_total / (1 - margen_decimal) if margen_decimal < 1 else evento.costo_total

        # Si no hay precio final, usar propuesta
        if not evento.precio_final or evento.precio_final == 0:
            evento.precio_final = evento.precio_propuesta

        # Calcular saldo
        evento.saldo = float(evento.precio_final or 0) - float(evento.anticipo or 0)

    @staticmethod
    def actualizar_evento(evento_id, data):
        """
        Actualiza un evento existente

        Args:
            evento_id: ID del evento
            data: dict con campos a actualizar

        Returns:
            tuple: (success, evento/error, mensaje)
        """
        try:
            evento = Evento.query.get(evento_id)
            if not evento:
                return False, None, 'Evento no encontrado'

            # Actualizar campos permitidos
            campos_actualizables = [
                'cliente_nombre', 'cliente_telefono', 'cliente_email',
                'nombre_evento', 'tipo_evento', 'hora_evento', 'lugar_evento',
                'cantidad_personas', 'costo_mano_obra', 'costo_transporte',
                'costo_otros', 'margen_porcentaje', 'notas_cotizacion', 'notas_internas'
            ]

            for campo in campos_actualizables:
                if campo in data:
                    setattr(evento, campo, data[campo])

            # Fecha evento requiere parsing especial
            if 'fecha_evento' in data:
                evento.fecha_evento = datetime.fromisoformat(data['fecha_evento']) if data['fecha_evento'] else None

            # Recalcular costos
            EventosService.recalcular_costos_evento(evento)

            db.session.commit()

            return True, evento, 'Evento actualizado exitosamente'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def agregar_insumo(evento_id, data):
        """
        Agrega un insumo al evento

        Args:
            evento_id: ID del evento
            data: dict con tipo_insumo (o insumo_tipo), cantidad, costo_unitario, y referencias específicas

        Returns:
            tuple: (success, evento/error, mensaje)
        """
        try:
            evento = Evento.query.get(evento_id)
            if not evento:
                return False, None, 'Evento no encontrado'

            # Obtener tipo de insumo (acepta ambos nombres para compatibilidad)
            tipo_insumo = data.get('tipo_insumo') or data.get('insumo_tipo')
            if not tipo_insumo:
                return False, None, 'Campo requerido: tipo_insumo'

            cantidad = data.get('cantidad', 1)
            costo_unitario = data.get('costo_unitario', 0)
            notas = data.get('notas', '')

            # Crear insumo de evento
            insumo_evento = EventoInsumo(
                evento_id=evento_id,
                tipo_insumo=tipo_insumo,
                cantidad=cantidad,
                costo_unitario=costo_unitario,
                costo_total=costo_unitario * cantidad,
                notas=notas
            )

            # Asignar referencias según tipo
            if tipo_insumo == 'flor' and data.get('flor_id'):
                insumo_evento.flor_id = str(data['flor_id'])
            elif tipo_insumo == 'contenedor' and data.get('contenedor_id'):
                insumo_evento.contenedor_id = str(data['contenedor_id'])
            elif tipo_insumo == 'producto' and data.get('producto_id'):
                # Los productos tienen ID numérico
                insumo_evento.producto_id = int(data['producto_id'])
            elif tipo_insumo == 'producto_evento' and data.get('producto_evento_id'):
                insumo_evento.producto_evento_id = int(data['producto_evento_id'])
            elif tipo_insumo in ['mano_obra', 'transporte', 'otro'] and data.get('nombre_otro'):
                insumo_evento.nombre_otro = data['nombre_otro']

            db.session.add(insumo_evento)

            # Recalcular costos del evento
            db.session.flush()  # Para que el insumo esté disponible
            EventosService.recalcular_costos_evento(evento)

            db.session.commit()

            return True, evento, 'Insumo agregado exitosamente'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def eliminar_evento(evento_id):
        """
        Elimina un evento y todos sus insumos

        Args:
            evento_id: ID del evento

        Returns:
            tuple: (success, mensaje)
        """
        try:
            evento = Evento.query.get(evento_id)
            if not evento:
                return False, 'Evento no encontrado'

            # Eliminar todos los insumos del evento (cascade debería hacerlo automáticamente, pero lo hacemos explícito)
            from models.evento import EventoInsumo
            try:
                # Intentar eliminar insumos explícitamente
                insumos_eliminados = EventoInsumo.query.filter_by(evento_id=evento_id).delete(synchronize_session=False)
                db.session.flush()  # Aplicar cambios de insumos antes de eliminar el evento
            except Exception as e:
                # Si falla, intentar eliminar uno por uno
                print(f"⚠️ Error eliminando insumos en batch, intentando uno por uno: {str(e)}")
                for insumo in evento.insumos:
                    try:
                        db.session.delete(insumo)
                    except Exception as e2:
                        print(f"⚠️ Error eliminando insumo {insumo.id}: {str(e2)}")
                db.session.flush()

            # Eliminar el evento
            db.session.delete(evento)
            db.session.commit()

            return True, 'Evento eliminado exitosamente'

        except Exception as e:
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False, str(e)

    @staticmethod
    def eliminar_insumo(evento_id, insumo_id):
        """
        Elimina un insumo del evento

        Args:
            evento_id: ID del evento
            insumo_id: ID del insumo de evento

        Returns:
            tuple: (success, evento/error, mensaje)
        """
        try:
            evento = Evento.query.get(evento_id)
            if not evento:
                return False, None, 'Evento no encontrado'

            insumo = EventoInsumo.query.get(insumo_id)
            if not insumo or insumo.evento_id != evento_id:
                return False, None, 'Insumo no encontrado'

            db.session.delete(insumo)
            db.session.flush()

            # Recalcular costos
            EventosService.recalcular_costos_evento(evento)

            db.session.commit()

            return True, evento, 'Insumo eliminado exitosamente'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def cambiar_estado(evento_id, nuevo_estado):
        """
        Cambia el estado de un evento

        Args:
            evento_id: ID del evento
            nuevo_estado: nuevo estado del evento

        Returns:
            tuple: (success, evento/error, mensaje)
        """
        try:
            evento = Evento.query.get(evento_id)
            if not evento:
                return False, None, 'Evento no encontrado'

            evento.estado = nuevo_estado
            db.session.commit()

            return True, evento, f'Estado actualizado a {nuevo_estado}'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def reservar_insumos(evento_id):
        """
        Reserva los insumos del evento (marca como 'en_evento')

        Args:
            evento_id: ID del evento

        Returns:
            tuple: (success, mensaje_detalle, mensaje)
        """
        try:
            evento = Evento.query.get(evento_id)
            if not evento:
                return False, None, 'Evento no encontrado'

            reservados = []
            faltantes = []

            for insumo in evento.insumos:
                if insumo.insumo_tipo == 'Flor':
                    flor = Flor.query.get(insumo.insumo_id)
                    if flor:
                        if flor.cantidad_disponible >= insumo.cantidad:
                            flor.cantidad_en_evento += insumo.cantidad
                            reservados.append(f"Flor {flor.tipo} {flor.color}: {insumo.cantidad}")
                        else:
                            faltantes.append(f"Flor {flor.tipo} {flor.color}: necesita {insumo.cantidad}, disponible {flor.cantidad_disponible}")
                else:  # Contenedor
                    contenedor = Contenedor.query.get(insumo.insumo_id)
                    if contenedor:
                        if contenedor.cantidad_disponible >= insumo.cantidad:
                            contenedor.cantidad_en_evento += insumo.cantidad
                            reservados.append(f"Contenedor {contenedor.tipo}: {insumo.cantidad}")
                        else:
                            faltantes.append(f"Contenedor {contenedor.tipo}: necesita {insumo.cantidad}, disponible {contenedor.cantidad_disponible}")

            if faltantes:
                db.session.rollback()
                return False, faltantes, 'Stock insuficiente para algunos insumos'

            db.session.commit()
            return True, reservados, 'Insumos reservados exitosamente'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def descontar_stock(evento_id):
        """
        Descuenta el stock de los insumos del evento (ya no están disponibles)

        Args:
            evento_id: ID del evento

        Returns:
            tuple: (success, mensaje_detalle, mensaje)
        """
        try:
            evento = Evento.query.get(evento_id)
            if not evento:
                return False, None, 'Evento no encontrado'

            descontados = []

            for insumo in evento.insumos:
                if insumo.insumo_tipo == 'Flor':
                    flor = Flor.query.get(insumo.insumo_id)
                    if flor:
                        # Reducir de en_evento y de stock
                        flor.cantidad_en_evento = max(0, flor.cantidad_en_evento - insumo.cantidad)
                        flor.cantidad_stock = max(0, flor.cantidad_stock - insumo.cantidad)
                        descontados.append(f"Flor {flor.tipo} {flor.color}: -{insumo.cantidad}")
                else:  # Contenedor
                    contenedor = Contenedor.query.get(insumo.insumo_id)
                    if contenedor:
                        contenedor.cantidad_en_evento = max(0, contenedor.cantidad_en_evento - insumo.cantidad)
                        contenedor.stock = max(0, contenedor.stock - insumo.cantidad)
                        descontados.append(f"Contenedor {contenedor.tipo}: -{insumo.cantidad}")

            db.session.commit()
            return True, descontados, 'Stock descontado exitosamente'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def marcar_devuelto(evento_id):
        """
        Marca los insumos como devueltos (regresa al stock)

        Args:
            evento_id: ID del evento

        Returns:
            tuple: (success, mensaje_detalle, mensaje)
        """
        try:
            evento = Evento.query.get(evento_id)
            if not evento:
                return False, None, 'Evento no encontrado'

            devueltos = []

            for insumo in evento.insumos:
                if insumo.insumo_tipo == 'Flor':
                    flor = Flor.query.get(insumo.insumo_id)
                    if flor:
                        flor.cantidad_en_evento = max(0, flor.cantidad_en_evento - insumo.cantidad)
                        flor.cantidad_stock += insumo.cantidad
                        devueltos.append(f"Flor {flor.tipo} {flor.color}: +{insumo.cantidad}")
                else:  # Contenedor
                    contenedor = Contenedor.query.get(insumo.insumo_id)
                    if contenedor:
                        contenedor.cantidad_en_evento = max(0, contenedor.cantidad_en_evento - insumo.cantidad)
                        contenedor.stock += insumo.cantidad
                        devueltos.append(f"Contenedor {contenedor.tipo}: +{insumo.cantidad}")

            db.session.commit()
            return True, devueltos, 'Insumos devueltos al stock'

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    @staticmethod
    def obtener_productos_evento():
        """
        Obtiene todos los productos de eventos activos

        Returns:
            list: productos de eventos
        """
        productos = ProductoEvento.query.filter_by(activo=True).all()
        return productos

    @staticmethod
    def generar_html_cotizacion(evento):
        """
        Genera HTML imprimible para la cotización del evento
        
        Args:
            evento: Evento - objeto del evento con insumos cargados
            
        Returns:
            str: HTML
        """
        from datetime import datetime
        
        # Formatear fecha
        fecha_str = evento.fecha_evento.strftime('%d/%m/%Y') if evento.fecha_evento else 'Sin fecha'
        hora_str = evento.hora_evento or 'Sin hora'
        
        # Calcular totales
        costo_total = float(evento.costo_total or 0)
        precio_propuesta = float(evento.precio_propuesta or 0)
        margen = float(evento.margen_porcentaje or 30)
        
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cotización {evento.id} - {evento.nombre_evento}</title>
    <style>
        @media print {{
            @page {{ margin: 1.5cm; }}
            body {{ margin: 0; }}
        }}
        body {{
            font-family: Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 30px;
            font-size: 12px;
            color: #333;
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #e91e63;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #e91e63;
            margin: 0;
            font-size: 28px;
        }}
        .header p {{
            color: #666;
            margin: 5px 0;
        }}
        .info-section {{
            margin-bottom: 25px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 8px;
            border-left: 4px solid #e91e63;
        }}
        .info-section h2 {{
            color: #e91e63;
            margin-top: 0;
            margin-bottom: 15px;
            font-size: 18px;
            border-bottom: 2px solid #e91e63;
            padding-bottom: 5px;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        .info-item {{
            margin-bottom: 10px;
        }}
        .info-item label {{
            font-weight: bold;
            color: #555;
            display: block;
            margin-bottom: 3px;
            font-size: 11px;
        }}
        .info-item p {{
            margin: 0;
            color: #333;
            font-size: 13px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
        }}
        th {{
            background: #e91e63;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
            font-size: 12px;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #ddd;
            font-size: 11px;
        }}
        tr:nth-child(even) {{
            background: #f9f9f9;
        }}
        .total-row {{
            background: #fff5f5 !important;
            font-weight: bold;
            font-size: 13px;
        }}
        .financial-section {{
            margin-top: 30px;
            padding: 20px;
            background: linear-gradient(135deg, #fff5f5 0%, #ffeef5 100%);
            border-radius: 8px;
            border: 2px solid #e91e63;
        }}
        .financial-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 20px;
            margin-top: 15px;
        }}
        .financial-item {{
            text-align: center;
        }}
        .financial-item label {{
            display: block;
            font-size: 11px;
            color: #666;
            margin-bottom: 5px;
        }}
        .financial-item .value {{
            font-size: 24px;
            font-weight: bold;
            color: #e91e63;
        }}
        .notes {{
            margin-top: 25px;
            padding: 15px;
            background: #fff9e6;
            border-left: 4px solid #ffc107;
            border-radius: 4px;
        }}
        .notes h3 {{
            margin-top: 0;
            color: #856404;
            font-size: 14px;
        }}
        .notes p {{
            margin: 0;
            color: #333;
            font-size: 12px;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🌸 Las Lira - Cotización de Evento</h1>
        <p>Cotización #{evento.id} | Fecha de emisión: {datetime.now().strftime('%d/%m/%Y')}</p>
    </div>

    <!-- Información del Cliente -->
    <div class="info-section">
        <h2>👤 Información del Cliente</h2>
        <div class="info-grid">
            <div class="info-item">
                <label>Nombre:</label>
                <p>{evento.cliente_nombre or '-'}</p>
            </div>
            <div class="info-item">
                <label>Teléfono:</label>
                <p>{evento.cliente_telefono or '-'}</p>
            </div>
            <div class="info-item">
                <label>Email:</label>
                <p>{evento.cliente_email or '-'}</p>
            </div>
        </div>
    </div>

    <!-- Información del Evento -->
    <div class="info-section">
        <h2>📅 Detalles del Evento</h2>
        <div class="info-grid">
            <div class="info-item">
                <label>Nombre del Evento:</label>
                <p>{evento.nombre_evento or '-'}</p>
            </div>
            <div class="info-item">
                <label>Tipo de Evento:</label>
                <p>{evento.tipo_evento or '-'}</p>
            </div>
            <div class="info-item">
                <label>Fecha:</label>
                <p>{fecha_str}</p>
            </div>
            <div class="info-item">
                <label>Hora:</label>
                <p>{hora_str}</p>
            </div>
            <div class="info-item">
                <label>Lugar:</label>
                <p>{evento.lugar_evento or '-'}</p>
            </div>
            <div class="info-item">
                <label>Cantidad de Personas:</label>
                <p>{evento.cantidad_personas or '-'}</p>
            </div>
        </div>
    </div>

    <!-- Desglose de Insumos -->
"""
        
        # Agregar tabla de insumos
        if evento.insumos and len(evento.insumos) > 0:
            html += """
    <div class="info-section">
        <h2>📦 Desglose de Insumos</h2>
        <table>
            <thead>
                <tr>
                    <th>Tipo</th>
                    <th>Descripción</th>
                    <th style="text-align: right;">Cantidad</th>
                    <th style="text-align: right;">Costo Unit.</th>
                    <th style="text-align: right;">Total</th>
                </tr>
            </thead>
            <tbody>
"""
            for insumo in evento.insumos:
                tipo = insumo.tipo_insumo or 'otro'
                descripcion = insumo.nombre_otro or f'Insumo {tipo}'
                
                # Intentar obtener descripción del insumo
                if tipo == 'flor' and insumo.flor_id:
                    flor = Flor.query.get(insumo.flor_id)
                    if flor:
                        descripcion = f"{flor.tipo} - {flor.color}"
                elif tipo == 'contenedor' and insumo.contenedor_id:
                    contenedor = Contenedor.query.get(insumo.contenedor_id)
                    if contenedor:
                        descripcion = f"{contenedor.tipo} - {contenedor.material}"
                elif tipo == 'producto' and insumo.producto_id:
                    producto = Producto.query.get(insumo.producto_id)
                    if producto:
                        descripcion = producto.nombre or producto.arreglo_pedido or f'Producto {insumo.producto_id}'
                
                cantidad = insumo.cantidad or 0
                costo_unit = float(insumo.costo_unitario or 0)
                total = cantidad * costo_unit
                
                html += f"""
                <tr>
                    <td>{tipo.replace('_', ' ').title()}</td>
                    <td>{descripcion}</td>
                    <td style="text-align: right;">{cantidad}</td>
                    <td style="text-align: right;">${costo_unit:,.0f}</td>
                    <td style="text-align: right;">${total:,.0f}</td>
                </tr>
"""
            
            html += f"""
                <tr class="total-row">
                    <td colspan="4" style="text-align: right; font-size: 14px;">TOTAL COSTO INSUMOS:</td>
                    <td style="text-align: right; font-size: 16px;">${costo_total:,.0f}</td>
                </tr>
            </tbody>
        </table>
    </div>
"""
        
        # Información financiera
        html += f"""
    <div class="financial-section">
        <h2 style="margin-top: 0; color: #e91e63; border-bottom: 2px solid #e91e63; padding-bottom: 10px;">💰 Información Financiera</h2>
        <div class="financial-grid">
            <div class="financial-item">
                <label>Costo Total</label>
                <div class="value" style="color: #333;">${costo_total:,.0f}</div>
            </div>
            <div class="financial-item">
                <label>Margen ({margen}%)</label>
                <div class="value" style="color: #e91e63;">${precio_propuesta - costo_total:,.0f}</div>
            </div>
            <div class="financial-item">
                <label>Precio Propuesta</label>
                <div class="value" style="color: #e91e63;">${precio_propuesta:,.0f}</div>
            </div>
        </div>
"""
        
        if evento.precio_final and evento.precio_final > 0:
            precio_final = float(evento.precio_final)
            anticipo = float(evento.anticipo or 0)
            saldo = float(evento.saldo or 0)
            
            html += f"""
        <div class="financial-grid" style="margin-top: 20px; padding-top: 20px; border-top: 2px solid #e91e63;">
            <div class="financial-item">
                <label>Precio Final</label>
                <div class="value" style="color: #28a745;">${precio_final:,.0f}</div>
            </div>
            <div class="financial-item">
                <label>Anticipo</label>
                <div class="value" style="color: #333;">${anticipo:,.0f}</div>
            </div>
            <div class="financial-item">
                <label>Saldo Pendiente</label>
                <div class="value" style="color: #ff9800;">${saldo:,.0f}</div>
            </div>
        </div>
"""
        
        html += """
    </div>
"""
        
        # Notas
        if evento.notas_cotizacion:
            html += f"""
    <div class="notes">
        <h3>📝 Notas de Cotización</h3>
        <p>{evento.notas_cotizacion}</p>
    </div>
"""
        
        html += """
    <div style="margin-top: 40px; text-align: center; color: #999; font-size: 10px; border-top: 1px solid #ddd; padding-top: 20px;">
        <p>Este documento es una cotización y no constituye una orden de compra hasta su confirmación.</p>
        <p>Las Lira - Sistema de Gestión de Florería</p>
    </div>
</body>
</html>
"""
        
        return html

    @staticmethod
    def generar_pdf_cotizacion(evento):
        """
        Genera un PDF de la cotización del evento
        
        Args:
            evento: Evento - objeto del evento con insumos cargados
            
        Returns:
            bytes: PDF en formato bytes
        """
        try:
            from weasyprint import HTML
            from io import BytesIO
            
            html = EventosService.generar_html_cotizacion(evento)
            pdf_buffer = BytesIO()
            HTML(string=html).write_pdf(pdf_buffer)
            pdf_buffer.seek(0)
            return pdf_buffer.getvalue()
        except Exception as e:
            raise Exception(f"Error al generar PDF de cotización: {str(e)}")
