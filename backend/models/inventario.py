"""
Modelos de Inventario (Flores y Contenedores)
"""

from datetime import datetime, date
from extensions import db

class Flor(db.Model):
    __tablename__ = 'flores'
    
    id = db.Column(db.String(10), primary_key=True)
    tipo = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(30))
    nombre = db.Column(db.String(100))  # Nombre completo (ej: "Rosa Roja")
    ubicacion = db.Column(db.String(100))  # Taller, Bodega 1, etc.
    foto_url = db.Column(db.String(500))  # URL o nombre de archivo de la foto
    proveedor_id = db.Column(db.String(10), db.ForeignKey('proveedores.id'))
    costo_unitario = db.Column(db.Numeric(10, 2), default=0)
    cantidad_stock = db.Column(db.Integer, default=0, nullable=False)
    cantidad_en_uso = db.Column(db.Integer, default=0, nullable=False)  # Reservadas en pedidos confirmados
    cantidad_en_evento = db.Column(db.Integer, default=0, nullable=False)  # Reservadas en eventos
    # Las flores NO tienen bodega, se compran según necesidad
    unidad = db.Column(db.String(20), default='Tallos')
    fecha_actualizacion = db.Column(db.Date, default=date.today)
    
    @property
    def cantidad_disponible(self):
        """Cantidad disponible = stock total - cantidad en uso - cantidad en evento"""
        return self.cantidad_stock - self.cantidad_en_uso - self.cantidad_en_evento
    
    # Relaciones
    proveedor = db.relationship('Proveedor', backref='flores', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'color': self.color,
            'nombre': self.nombre or f"{self.tipo} {self.color}".strip(),
            'ubicacion': self.ubicacion,
            'foto_url': self.foto_url,
            'proveedor_id': self.proveedor_id,
            'proveedor_nombre': self.proveedor.nombre if self.proveedor else None,
            'costo_unitario': float(self.costo_unitario) if self.costo_unitario else 0,
            'cantidad_stock': self.cantidad_stock,
            'cantidad_en_uso': self.cantidad_en_uso,
            'cantidad_en_evento': self.cantidad_en_evento,
            'cantidad_disponible': self.cantidad_disponible,
            'unidad': self.unidad,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
    
    def __repr__(self):
        return f'<Flor {self.tipo} {self.color}>'


class Contenedor(db.Model):
    __tablename__ = 'contenedores'
    
    id = db.Column(db.String(10), primary_key=True)
    nombre = db.Column(db.String(100))  # Nombre completo del contenedor
    tipo = db.Column(db.String(50))  # Tipo flexible (no Enum)
    material = db.Column(db.String(30))
    forma = db.Column(db.String(30))
    tamano = db.Column(db.String(50))
    color = db.Column(db.String(30))
    ubicacion = db.Column(db.String(100))  # Bodega 1, Bodega 2, etc.
    foto_url = db.Column(db.String(500))  # URL o nombre de archivo de la foto
    costo = db.Column(db.Numeric(10, 2), default=0)
    cantidad_stock = db.Column(db.Integer, default=0, nullable=False)  # Renombrado de stock
    cantidad_en_uso = db.Column(db.Integer, default=0, nullable=False)  # Reservados en pedidos confirmados
    cantidad_en_evento = db.Column(db.Integer, default=0, nullable=False)  # Reservados en eventos
    bodega_id = db.Column(db.Integer, db.ForeignKey('bodegas.id'))  # Ahora opcional
    fecha_actualizacion = db.Column(db.Date, default=date.today)
    
    # Compatibilidad con código antiguo
    @property
    def stock(self):
        return self.cantidad_stock
    
    @stock.setter
    def stock(self, value):
        self.cantidad_stock = value
    
    @property
    def cantidad_disponible(self):
        """Cantidad disponible = stock total - cantidad en uso - cantidad en evento"""
        return self.stock - self.cantidad_en_uso - self.cantidad_en_evento
    
    # Relaciones
    bodega = db.relationship('Bodega', backref='contenedores', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre or f"{self.tipo or ''} {self.tamano or ''}".strip(),
            'tipo': self.tipo,
            'material': self.material,
            'forma': self.forma,
            'tamano': self.tamano,
            'color': self.color,
            'ubicacion': self.ubicacion,
            'foto_url': self.foto_url,
            'costo': float(self.costo) if self.costo else 0,
            'cantidad_stock': self.cantidad_stock,
            'stock': self.stock,  # Compatibilidad
            'cantidad_en_uso': self.cantidad_en_uso,
            'cantidad_en_evento': self.cantidad_en_evento,
            'cantidad_disponible': self.cantidad_disponible,
            'bodega_id': self.bodega_id,
            'bodega_nombre': self.bodega.nombre if self.bodega else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None
        }
    
    def __repr__(self):
        return f'<Contenedor {self.tipo} {self.forma}>'


class Bodega(db.Model):
    __tablename__ = 'bodegas'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    direccion = db.Column(db.String(200))
    encargado = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    activa = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'direccion': self.direccion,
            'encargado': self.encargado,
            'telefono': self.telefono,
            'activa': self.activa
        }
    
    def __repr__(self):
        return f'<Bodega {self.nombre}>'


class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.String(10), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(100))
    especialidad = db.Column(db.Text)
    dias_entrega = db.Column(db.String(200))
    notas = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'contacto': self.contacto,
            'telefono': self.telefono,
            'email': self.email,
            'especialidad': self.especialidad,
            'dias_entrega': self.dias_entrega,
            'notas': self.notas,
            'activo': self.activo
        }
    
    def __repr__(self):
        return f'<Proveedor {self.nombre}>'

