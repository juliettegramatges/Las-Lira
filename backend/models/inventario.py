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
    # proveedor_id removido - ahora se usa relación muchos-a-muchos
    costo_unitario = db.Column(db.Numeric(10, 2), default=0)
    cantidad_stock = db.Column(db.Integer, default=0, nullable=False)
    cantidad_en_uso = db.Column(db.Integer, default=0, nullable=False)  # Reservadas en pedidos confirmados
    cantidad_en_evento = db.Column(db.Integer, default=0, nullable=False)  # Reservadas en eventos
    stock_bajo = db.Column(db.Integer, default=10, nullable=False)  # Umbral de stock bajo (modificable)
    # Las flores NO tienen bodega, se compran según necesidad
    unidad = db.Column(db.String(20), default='Tallos')
    fecha_actualizacion = db.Column(db.Date, default=date.today)
    
    @property
    def cantidad_disponible(self):
        """Cantidad disponible = stock total - cantidad en uso - cantidad en evento"""
        return self.cantidad_stock - self.cantidad_en_uso - self.cantidad_en_evento
    
    # Relación muchos-a-muchos con proveedores (definida en Proveedor)
    
    def to_dict(self):
        return {
            'id': self.id,
            'tipo': self.tipo,
            'color': self.color,
            'nombre': self.nombre or f"{self.tipo} {self.color}".strip(),
            'ubicacion': self.ubicacion,
            'foto_url': self.foto_url,
            'costo_unitario': float(self.costo_unitario) if self.costo_unitario else 0,
            'cantidad_stock': self.cantidad_stock,
            'cantidad_en_uso': self.cantidad_en_uso,
            'cantidad_en_evento': self.cantidad_en_evento,
            'cantidad_disponible': self.cantidad_disponible,
            'stock_bajo': self.stock_bajo,
            'unidad': self.unidad,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'proveedores': [{'id': p.id, 'nombre': p.nombre, 'empresa': p.empresa} for p in self.proveedores] if hasattr(self, 'proveedores') else []
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
    stock_bajo = db.Column(db.Integer, default=5, nullable=False)  # Umbral de stock bajo (modificable)
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
        costo_valor = float(self.costo) if self.costo else 0
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
            'costo': costo_valor,
            'costo_unitario': costo_valor,  # Alias para compatibilidad con frontend
            'cantidad_stock': self.cantidad_stock,
            'stock': self.stock,  # Compatibilidad
            'cantidad_en_uso': self.cantidad_en_uso,
            'cantidad_en_evento': self.cantidad_en_evento,
            'cantidad_disponible': self.cantidad_disponible,
            'stock_bajo': self.stock_bajo,
            'bodega_id': self.bodega_id,
            'bodega_nombre': self.bodega.nombre if self.bodega else None,
            'fecha_actualizacion': self.fecha_actualizacion.isoformat() if self.fecha_actualizacion else None,
            'proveedores': [{'id': p.id, 'nombre': p.nombre, 'empresa': p.empresa} for p in self.proveedores] if hasattr(self, 'proveedores') else []
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


# Tabla de relación muchos-a-muchos entre Proveedor y Flor
proveedor_flor = db.Table('proveedor_flor',
    db.Column('proveedor_id', db.String(10), db.ForeignKey('proveedores.id'), primary_key=True),
    db.Column('flor_id', db.String(10), db.ForeignKey('flores.id'), primary_key=True)
)

# Tabla de relación muchos-a-muchos entre Proveedor y Contenedor
proveedor_contenedor = db.Table('proveedor_contenedor',
    db.Column('proveedor_id', db.String(10), db.ForeignKey('proveedores.id'), primary_key=True),
    db.Column('contenedor_id', db.String(10), db.ForeignKey('contenedores.id'), primary_key=True)
)

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.String(10), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    contacto = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    empresa = db.Column(db.String(100))  # 🆕 Campo empresa
    email = db.Column(db.String(100))
    especialidad = db.Column(db.Text)
    dias_entrega = db.Column(db.String(200))
    notas = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones muchos-a-muchos
    flores = db.relationship('Flor', secondary=proveedor_flor, backref=db.backref('proveedores', lazy='dynamic'), lazy='dynamic')
    contenedores = db.relationship('Contenedor', secondary=proveedor_contenedor, backref=db.backref('proveedores', lazy='dynamic'), lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'contacto': self.contacto,
            'telefono': self.telefono,
            'empresa': self.empresa,
            'email': self.email,
            'especialidad': self.especialidad,
            'dias_entrega': self.dias_entrega,
            'notas': self.notas,
            'activo': self.activo,
            'total_flores': self.flores.count() if hasattr(self.flores, 'count') else len(list(self.flores)),
            'total_contenedores': self.contenedores.count() if hasattr(self.contenedores, 'count') else len(list(self.contenedores))
        }
    
    def to_dict_con_insumos(self):
        """Versión con lista de insumos asociados"""
        dict_base = self.to_dict()
        dict_base['flores'] = [{'id': f.id, 'nombre': f.nombre} for f in self.flores]
        dict_base['contenedores'] = [{'id': c.id, 'nombre': c.nombre} for c in self.contenedores]
        return dict_base
    
    def __repr__(self):
        return f'<Proveedor {self.nombre}>'

