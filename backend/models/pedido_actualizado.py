"""
Modelo de Pedido Actualizado - Versión flexible para datos históricos
"""

from datetime import datetime
from extensions import db

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.String(20), primary_key=True)
    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    fecha_entrega = db.Column(db.DateTime)
    canal = db.Column(db.String(20), nullable=False, default='WhatsApp')  # Shopify, WhatsApp, etc.
    shopify_order_number = db.Column(db.String(50))
    
    # Cliente - Relación con tabla de clientes
    cliente_id = db.Column(db.String(10), db.ForeignKey('clientes.id'))
    cliente_nombre = db.Column(db.String(200), nullable=False)
    cliente_telefono = db.Column(db.String(50))
    cliente_email = db.Column(db.String(200))
    
    # Producto
    producto_id = db.Column(db.String(10), db.ForeignKey('productos.id'))
    arreglo_pedido = db.Column(db.String(300))  # Nombre del arreglo/producto
    detalles_adicionales = db.Column(db.Text)
    
    # Precios
    precio_ramo = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    precio_envio = db.Column(db.Numeric(10, 2), default=0)
    
    # Destinatario y mensaje
    destinatario = db.Column(db.String(200))
    mensaje = db.Column(db.Text)
    firma = db.Column(db.String(200))
    
    # Dirección y ubicación
    direccion_entrega = db.Column(db.String(500))
    comuna = db.Column(db.String(100))
    motivo = db.Column(db.String(100))  # Cumpleaños, Aniversario, Difunto, etc.
    
    # Estado - Más flexible para datos históricos
    estado = db.Column(db.String(50), default='Pedidos Semana')
    # Opciones: Entregas de Hoy, Entregas para Mañana, En Proceso, 
    #           Listo para Despacho, Despachados, Pedidos Semana, 
    #           Eventos, Archivado, Cancelado, ACTIVO, ARCHIVADO
    
    # Información de entrega y pago
    dia_entrega = db.Column(db.String(20))
    estado_pago = db.Column(db.String(50), default='No Pagado')
    # Opciones: Pagado, No Pagado, Pendiente, PAGADO, PENDIENTE
    
    tipo_pedido = db.Column(db.String(100))  # EVENTO, MANTENCIONES, etc.
    
    # Cobranza
    cobranza = db.Column(db.String(300))
    plazo_pago_dias = db.Column(db.Integer, default=0)
    fecha_maxima_pago = db.Column(db.DateTime)
    
    # Método de pago - Flexible
    metodo_pago = db.Column(db.String(100))
    # Opciones: Tr. BICE, Tr. Santander, Tr. Itaú, Transferencia, 
    #           Pago confirmado, Pago con tarjeta, Pendiente, TRANSFERENCIA, EFECTIVO, etc.
    
    # Documento tributario - Flexible
    documento_tributario = db.Column(db.String(100))
    # Opciones: Hacer boleta, Hacer factura, Boleta emitida, Factura emitida, 
    #           No requiere, BOLETA, FACTURA, etc.
    numero_documento = db.Column(db.String(50))
    
    # Información adicional de datos históricos
    tipo_entrega = db.Column(db.String(20))  # ENVÍO, RETIRO
    match_score = db.Column(db.String(200))  # Score de asociación con producto
    insumos_extraidos = db.Column(db.Text)  # Insumos identificados en personalizaciones
    dimensiones = db.Column(db.String(100))  # Dimensiones del producto
    contenedor = db.Column(db.String(100))  # Tipo de contenedor
    colores = db.Column(db.String(200))  # Colores del producto
    
    # Metadatos
    foto_enviado_url = db.Column(db.String(500))
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
            'tipo_entrega': self.tipo_entrega,
            'match_score': self.match_score,
            'insumos_extraidos': self.insumos_extraidos,
            'dimensiones': self.dimensiones,
            'contenedor': self.contenedor,
            'colores': self.colores,
            'foto_enviado_url': self.foto_enviado_url,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
        }
    
    def __repr__(self):
        return f'<Pedido {self.id} - {self.cliente_nombre}>'


class PedidoInsumo(db.Model):
    __tablename__ = 'pedidos_insumos'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.String(20), db.ForeignKey('pedidos.id'), nullable=False)
    insumo_tipo = db.Column(db.String(20), nullable=False)  # Flor, Contenedor, etc.
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

