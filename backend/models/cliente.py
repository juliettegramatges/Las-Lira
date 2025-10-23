"""
Modelo de Cliente para gestión de base de datos de clientes
"""

from backend.app import db
from datetime import datetime

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.String(10), primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    telefono = db.Column(db.String(20), nullable=False, unique=True)
    email = db.Column(db.String(200))
    
    # Tipo de cliente / Etiquetas
    tipo_cliente = db.Column(
        db.Enum('Nuevo', 'Fiel', 'Cumplidor', 'No Cumplidor', 'VIP', 'Ocasional', name='tipo_cliente_enum'),
        default='Nuevo',
        nullable=False
    )
    
    # Información adicional
    direccion_principal = db.Column(db.Text)
    notas = db.Column(db.Text)
    
    # Estadísticas
    total_pedidos = db.Column(db.Integer, default=0)
    total_gastado = db.Column(db.Numeric(10, 2), default=0)
    
    # Fechas
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    ultima_compra = db.Column(db.DateTime)
    
    # Relación con pedidos
    pedidos = db.relationship('Pedido', back_populates='cliente', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'telefono': self.telefono,
            'email': self.email,
            'tipo_cliente': self.tipo_cliente,
            'direccion_principal': self.direccion_principal,
            'notas': self.notas,
            'total_pedidos': self.total_pedidos,
            'total_gastado': float(self.total_gastado) if self.total_gastado else 0,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None,
            'ultima_compra': self.ultima_compra.isoformat() if self.ultima_compra else None
        }

