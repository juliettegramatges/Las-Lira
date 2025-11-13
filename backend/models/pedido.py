"""
Modelo de Pedido
"""

import os
from datetime import datetime
from extensions import db

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # ID único autoincremental
    numero_pedido = db.Column(db.String(20))  # Ej: "PED-00027" (puede repetirse)
    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_entrega = db.Column(db.DateTime, nullable=False)
    canal = db.Column(db.String(50), nullable=False, default='WhatsApp')  # Flexible para datos históricos
    shopify_order_number = db.Column(db.String(50))  # Ej: "#SH1234"
    # Cliente - Relación con tabla de clientes
    cliente_id = db.Column(db.String(10), db.ForeignKey('clientes.id'))
    # Datos del cliente (se mantienen por compatibilidad)
    cliente_nombre = db.Column(db.String(100), nullable=False)
    cliente_telefono = db.Column(db.String(20), nullable=False)
    cliente_email = db.Column(db.String(100))
    # Producto
    producto_id = db.Column(db.String(10), db.ForeignKey('productos.id'))
    arreglo_pedido = db.Column(db.String(200))  # Nombre textual del arreglo
    detalles_adicionales = db.Column(db.Text)
    # Precios
    precio_ramo = db.Column(db.Numeric(10, 2), nullable=False)
    precio_envio = db.Column(db.Numeric(10, 2), default=0)
    # Destinatario y mensaje
    destinatario = db.Column(db.String(100))  # Para quién es el arreglo
    mensaje = db.Column(db.Text)  # Mensaje en la tarjeta
    firma = db.Column(db.String(100))  # Firma del mensaje
    # Dirección y motivo
    direccion_entrega = db.Column(db.String(300), nullable=False)
    comuna = db.Column(db.String(100))  # Comuna de entrega
    latitud = db.Column(db.Float)  # Latitud GPS para optimización de rutas
    longitud = db.Column(db.Float)  # Longitud GPS para optimización de rutas
    motivo = db.Column(db.String(50))  # Cumpleaños, Aniversario, etc.
    # Estado (según flujo del Trello - ordenado por prioridad)
    # Cambiado a String para soportar datos históricos variados
    estado = db.Column(db.String(50), default='Pedidos Semana', nullable=False)
    # Etiquetas (días de semana, estado de pago, tipo)
    dia_entrega = db.Column(db.String(20))  # LUNES, MARTES, etc.
    estado_pago = db.Column(db.String(50), default='No Pagado')  # Flexible para datos históricos
    tipo_pedido = db.Column(db.String(50))  # EVENTO, MANTENCIONES, etc.
    # Cobranza detallada
    cobranza = db.Column(db.String(200))  # Legado (mantener por compatibilidad)
    plazo_pago_dias = db.Column(db.Integer, default=0)  # Días de plazo para pagar
    fecha_maxima_pago = db.Column(db.DateTime)  # Fecha límite para pagar (calculada)
    # 💰 Pago - Estado del pago (flexible para datos históricos)
    metodo_pago = db.Column(db.String(100), default='Pendiente')
    # 🧾 Documento tributario (flexible para datos históricos)
    documento_tributario = db.Column(db.String(100), default='Hacer boleta')
    numero_documento = db.Column(db.String(50))  # Ej: "10301" o "FACT-2025-001"
    # Foto del arreglo enviado (trazabilidad)
    foto_enviado_url = db.Column(db.String(500))  # Foto tomada antes de enviar
    # Información de Evento
    es_evento = db.Column(db.Boolean, default=False)  # Si es un pedido de evento
    tipo_evento = db.Column(db.String(50))  # Matrimonio, Funeral, Cumpleaños, etc.

    # Prioridad de entrega
    es_urgente = db.Column(db.Boolean, default=False)  # Pedido marcado como urgente
    
    # Retiro en tienda
    retiro_en_tienda = db.Column(db.Boolean, default=False)  # Si el pedido se retira en tienda

    # Información de Personalización
    colores_solicitados = db.Column(db.Text)  # JSON: ['Rojo', 'Blanco', 'Verde']
    tipo_personalizacion = db.Column(db.String(100))  # 'Ramo', 'Centro de Mesa', 'Arreglo Especial', etc.
    notas_personalizacion = db.Column(db.Text)  # Notas específicas de la personalización
    
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    cliente = db.relationship('Cliente', back_populates='pedidos', lazy=True)
    producto = db.relationship('Producto', backref='pedidos', lazy=True)
    insumos = db.relationship('PedidoInsumo', backref='pedido', lazy=True, cascade='all, delete-orphan')
    
    @property
    def precio_total(self):
        """Calcula precio total (ramo + envío)"""
        return (self.precio_ramo or 0) + (self.precio_envio or 0)
    
    def _obtener_imagen_producto(self):
        """Obtiene la imagen del producto con fallbacks"""
        if not self.producto:
            return None
        
        # 1. Intentar imagen_principal (nueva estructura consolidada)
        if self.producto.imagen_principal:
            return self.producto.imagen_principal
        
        # 2. Intentar imagen_url (estructura anterior)
        if self.producto.imagen_url:
            return self.producto.imagen_url
        
        # 3. Intentar obtener de la tabla imagenes_productos
        try:
            import sqlite3
            # Obtener la ruta del proyecto dinámicamente
            backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(os.path.dirname(backend_dir), 'las_lira.db')
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT url FROM imagenes_productos 
                WHERE producto_id = ? AND es_principal = 1
                LIMIT 1
            ''', (self.producto_id,))
            
            resultado = cursor.fetchone()
            conn.close()
            
            if resultado:
                return resultado[0]
        except Exception:
            pass  # Si hay error, continuar con None
        
        return None
    
    def to_dict(self):
        """Convierte el pedido a diccionario"""
        # Construir lista de productos con sus insumos
        productos_list = []
        for pp in self.pedido_productos:
            # Obtener insumos asociados a este producto
            insumos_producto = [insumo.to_dict() for insumo in pp.insumos]

            # Obtener imagen del producto
            producto_imagen = None
            if pp.producto:
                if pp.producto.imagen_principal:
                    producto_imagen = pp.producto.imagen_principal
                elif pp.producto.imagen_url:
                    producto_imagen = pp.producto.imagen_url

            productos_list.append({
                'id': pp.id,
                'producto_id': pp.producto_id,
                'producto_nombre': pp.producto_nombre,
                'precio': float(pp.precio),
                'cantidad': pp.cantidad,
                'foto_respaldo': pp.foto_respaldo,
                'producto_imagen': producto_imagen,
                'insumos': insumos_producto
            })

        return {
            'id': self.id,
            'fecha_pedido': self.fecha_pedido.isoformat() if self.fecha_pedido else None,
            'fecha_entrega': self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            'canal': self.canal,
            'shopify_order_number': self.shopify_order_number,
            'cliente_id': self.cliente_id,
            'cliente_nombre': self.cliente_nombre,
            'cliente_telefono': self.cliente_telefono,
            'cliente_email': self.cliente_email,
            'cliente_tipo': self.cliente.tipo_cliente if self.cliente else None,
            'producto_id': self.producto_id,
            'producto_nombre': self.producto.nombre if self.producto else None,
            'producto_imagen': self._obtener_imagen_producto(),
            'arreglo_pedido': self.arreglo_pedido,
            'detalles_adicionales': self.detalles_adicionales,
            'precio_ramo': float(self.precio_ramo) if self.precio_ramo else 0,
            'precio_envio': float(self.precio_envio) if self.precio_envio else 0,
            'precio_total': float(self.precio_total),
            'destinatario': self.destinatario,
            'mensaje': self.mensaje,
            'firma': self.firma,
            'direccion_entrega': self.direccion_entrega,
            'comuna': self.comuna,
            'latitud': self.latitud,
            'longitud': self.longitud,
            'motivo': self.motivo,
            'estado': self.estado,
            'dia_entrega': self.dia_entrega,
            'estado_pago': self.estado_pago,
            'tipo_pedido': self.tipo_pedido,
            'cobranza': self.cobranza,
            'plazo_pago_dias': self.plazo_pago_dias,
            'fecha_maxima_pago': self.fecha_maxima_pago.isoformat() if self.fecha_maxima_pago else None,
            'metodo_pago': self.metodo_pago,
            'documento_tributario': self.documento_tributario,
            'numero_documento': self.numero_documento,
            'foto_enviado_url': self.foto_enviado_url,
            'es_evento': self.es_evento,
            'tipo_evento': self.tipo_evento,
            'es_urgente': self.es_urgente,
            'colores_solicitados': self.colores_solicitados,
            'tipo_personalizacion': self.tipo_personalizacion,
            'notas_personalizacion': self.notas_personalizacion,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'productos': productos_list  # Lista de productos con sus insumos
        }
    
    def __repr__(self):
        return f'<Pedido {self.id} - {self.cliente_nombre}>'


class PedidoProducto(db.Model):
    """Tabla intermedia para múltiples productos en un pedido"""
    __tablename__ = 'pedidos_productos'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    producto_id = db.Column(db.String(10), db.ForeignKey('productos.id'), nullable=False)
    producto_nombre = db.Column(db.String(200))
    precio = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    foto_respaldo = db.Column(db.String(500))  # Foto de respaldo para este producto específico
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    pedido = db.relationship('Pedido', backref='pedido_productos', lazy=True)
    producto = db.relationship('Producto', backref='pedido_productos', lazy=True)
    insumos = db.relationship('PedidoInsumo', back_populates='pedido_producto', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'producto_id': self.producto_id,
            'producto_nombre': self.producto_nombre,
            'precio': float(self.precio),
            'cantidad': self.cantidad,
            'foto_respaldo': self.foto_respaldo,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }


class HistorialEstado(db.Model):
    """Tabla para registrar el historial de cambios de estado de pedidos"""
    __tablename__ = 'historial_estados'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    estado_anterior = db.Column(db.String(50), nullable=False)
    estado_nuevo = db.Column(db.String(50), nullable=False)
    fecha_cambio = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    usuario = db.Column(db.String(100))  # Opcional: quién hizo el cambio
    notas = db.Column(db.Text)  # Opcional: notas sobre el cambio

    # Relación
    pedido = db.relationship('Pedido', backref='historial_estados', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'estado_anterior': self.estado_anterior,
            'estado_nuevo': self.estado_nuevo,
            'fecha_cambio': self.fecha_cambio.isoformat() if self.fecha_cambio else None,
            'usuario': self.usuario,
            'notas': self.notas
        }

    def __repr__(self):
        return f'<HistorialEstado Pedido#{self.pedido_id}: {self.estado_anterior} → {self.estado_nuevo}>'


class PedidoInsumo(db.Model):
    __tablename__ = 'pedidos_insumos'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)  # Cambio a Integer
    pedido_producto_id = db.Column(db.Integer, db.ForeignKey('pedidos_productos.id'), nullable=True)  # Asociar a producto específico
    insumo_tipo = db.Column(db.Enum('Flor', 'Contenedor', name='insumo_tipo_enum'), nullable=False)
    insumo_id = db.Column(db.String(10), nullable=False)
    insumo_nombre = db.Column(db.String(200))  # Nombre del insumo para histórico
    cantidad = db.Column(db.Integer, nullable=False)
    costo_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    costo_total = db.Column(db.Numeric(10, 2), nullable=False)
    descontado_stock = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)

    # Relaciones
    pedido_producto = db.relationship('PedidoProducto', back_populates='insumos', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'pedido_producto_id': self.pedido_producto_id,
            'insumo_tipo': self.insumo_tipo,
            'insumo_id': self.insumo_id,
            'insumo_nombre': self.insumo_nombre,
            'cantidad': self.cantidad,
            'costo_unitario': float(self.costo_unitario),
            'costo_total': float(self.costo_total),
            'descontado_stock': self.descontado_stock,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }

