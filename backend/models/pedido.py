"""
Modelo de Pedido
"""

from datetime import datetime
from backend.app import db

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.String(20), primary_key=True)
    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    canal = db.Column(db.Enum('Shopify', 'WhatsApp', name='canal_enum'), nullable=False)
    cliente_nombre = db.Column(db.String(100), nullable=False)
    cliente_telefono = db.Column(db.String(20), nullable=False)
    cliente_email = db.Column(db.String(100))
    producto_id = db.Column(db.String(10), db.ForeignKey('productos.id'))
    descripcion_personalizada = db.Column(db.Text)
    estado = db.Column(
        db.Enum('Recibido', 'En Preparación', 'Listo', 'Despachado', 'Entregado', 'Cancelado', 
                name='estado_enum'),
        default='Recibido',
        nullable=False
    )
    precio_total = db.Column(db.Numeric(10, 2), nullable=False)
    direccion_entrega = db.Column(db.String(300), nullable=False)
    comuna = db.Column(db.String(50))
    fecha_entrega = db.Column(db.Date, nullable=False)
    hora_entrega = db.Column(db.Time)
    notas = db.Column(db.Text)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    producto = db.relationship('Producto', backref='pedidos', lazy=True)
    insumos = db.relationship('PedidoInsumo', backref='pedido', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convierte el pedido a diccionario"""
        return {
            'id': self.id,
            'fecha_pedido': self.fecha_pedido.isoformat() if self.fecha_pedido else None,
            'canal': self.canal,
            'cliente_nombre': self.cliente_nombre,
            'cliente_telefono': self.cliente_telefono,
            'cliente_email': self.cliente_email,
            'producto_id': self.producto_id,
            'producto_nombre': self.producto.nombre if self.producto else None,
            'descripcion_personalizada': self.descripcion_personalizada,
            'estado': self.estado,
            'precio_total': float(self.precio_total) if self.precio_total else 0,
            'direccion_entrega': self.direccion_entrega,
            'comuna': self.comuna,
            'fecha_entrega': self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            'hora_entrega': self.hora_entrega.isoformat() if self.hora_entrega else None,
            'notas': self.notas,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
        }
    
    def __repr__(self):
        return f'<Pedido {self.id} - {self.cliente_nombre}>'


class PedidoInsumo(db.Model):
    __tablename__ = 'pedidos_insumos'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.String(20), db.ForeignKey('pedidos.id'), nullable=False)
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

