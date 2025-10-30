"""
Modelo de Producto
"""

from datetime import datetime
from extensions import db

class Producto(db.Model):
    __tablename__ = 'productos'
    
    # Campos que realmente existen en la tabla
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2))
    categoria = db.Column(db.String(100))
    tipo = db.Column(db.String(100))
    imagen_url = db.Column(db.String(500))
    sku = db.Column(db.String(100))
    peso = db.Column(db.Numeric(10, 2))
    tags = db.Column(db.Text)
    metafields = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    imagen_principal = db.Column(db.String(500))
    
    # Relaciones
    recetas = db.relationship('RecetaProducto', backref='producto', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convierte el producto a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': float(self.precio) if self.precio else 0,
            'categoria': self.categoria,
            'tipo': self.tipo,
            'imagen_url': self.imagen_url,
            'imagen_principal': self.imagen_principal,
            'sku': self.sku,
            'peso': float(self.peso) if self.peso else 0,
            'tags': self.tags.split(',') if self.tags else [],
            'metafields': self.metafields,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'recetas': [r.to_dict() for r in self.recetas] if self.recetas else []
        }
    
    def __repr__(self):
        return f'<Producto {self.id} - {self.nombre}>'


class RecetaProducto(db.Model):
    __tablename__ = 'recetas_productos'
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.String(10), db.ForeignKey('productos.id'), nullable=False)
    insumo_tipo = db.Column(db.String(20), nullable=False)
    insumo_id = db.Column(db.String(10), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    unidad = db.Column(db.String(20), nullable=False)
    es_opcional = db.Column(db.Boolean, default=False)
    notas = db.Column(db.Text)
    
    def to_dict(self):
        # Obtener el nombre del insumo
        insumo_nombre = None
        insumo_costo = 0
        
        if self.insumo_tipo == 'Flor':
            from models.inventario import Flor
            flor = Flor.query.get(self.insumo_id)
            if flor:
                insumo_nombre = flor.nombre or f"{flor.tipo or ''} {flor.color or ''}".strip()
                insumo_costo = float(flor.costo_unitario) if flor.costo_unitario else 0
        elif self.insumo_tipo == 'Contenedor':
            from models.inventario import Contenedor
            contenedor = Contenedor.query.get(self.insumo_id)
            if contenedor:
                insumo_nombre = contenedor.nombre or contenedor.tipo or ''
                insumo_costo = float(contenedor.costo) if contenedor.costo else 0
        
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'insumo_tipo': self.insumo_tipo,
            'insumo_id': self.insumo_id,
            'insumo_nombre': insumo_nombre,
            'insumo_costo': insumo_costo,
            'cantidad': self.cantidad,
            'unidad': self.unidad,
            'es_opcional': self.es_opcional,
            'notas': self.notas
        }

