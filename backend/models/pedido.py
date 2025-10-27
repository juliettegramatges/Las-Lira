"""
Modelo de Pedido
"""

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
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    cliente = db.relationship('Cliente', back_populates='pedidos', lazy=True)
    producto = db.relationship('Producto', backref='pedidos', lazy=True)
    insumos = db.relationship('PedidoInsumo', backref='pedido', lazy=True, cascade='all, delete-orphan')
    
    @property
    def precio_total(self):
        """Calcula precio total (ramo + envío)"""
        return (self.precio_ramo or 0) + (self.precio_envio or 0)
    
    def to_dict(self):
        """Convierte el pedido a diccionario"""
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
            'producto_imagen': self.producto.imagen_url if self.producto else None,
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
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
        }
    
    def __repr__(self):
        return f'<Pedido {self.id} - {self.cliente_nombre}>'


class PedidoInsumo(db.Model):
    __tablename__ = 'pedidos_insumos'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)  # Cambio a Integer
    insumo_tipo = db.Column(db.Enum('Flor', 'Contenedor', name='insumo_tipo_enum'), nullable=False)
    insumo_id = db.Column(db.String(10), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    costo_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    costo_total = db.Column(db.Numeric(10, 2), nullable=False)
    descontado_stock = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'insumo_tipo': self.insumo_tipo,
            'insumo_id': self.insumo_id,
            'cantidad': self.cantidad,
            'costo_unitario': float(self.costo_unitario),
            'costo_total': float(self.costo_total),
            'descontado_stock': self.descontado_stock,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }

