"""
Modelo de Producto
"""

from datetime import datetime
from app import db

class Producto(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.String(10), primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    tipo_arreglo = db.Column(
        db.Enum('Con Florero', 'Con Macetero', 'Con Canasto', 'Sin Contenedor', 'Con Caja', 
                name='tipo_arreglo_enum'),
        nullable=False
    )
    # Nuevos campos detallados
    colores_asociados = db.Column(db.String(300))  # Ej: "Rojo, Verde oscuro, Burdeo"
    flores_asociadas = db.Column(db.String(300))  # Ej: "Rosa roja, Clavel rojo, Eucalipto"
    tipos_macetero = db.Column(db.String(200))  # Ej: "Florero vidrio cilíndrico"
    vista_360_180 = db.Column(db.String(3))  # "360" o "180"
    tamano = db.Column(db.String(20))  # Ej: "25 x 35" o "Ø 25"
    cuidados = db.Column(db.Text)  # Instrucciones detalladas de cuidado
    # Campos existentes
    precio_venta = db.Column(db.Numeric(10, 2), nullable=False)
    imagen_url = db.Column(db.String(500))
    disponible_shopify = db.Column(db.Boolean, default=True)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    recetas = db.relationship('RecetaProducto', backref='producto', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convierte el producto a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'tipo_arreglo': self.tipo_arreglo,
            'colores_asociados': self.colores_asociados,
            'flores_asociadas': self.flores_asociadas,
            'tipos_macetero': self.tipos_macetero,
            'vista_360_180': self.vista_360_180,
            'tamano': self.tamano,
            'cuidados': self.cuidados,
            'precio_venta': float(self.precio_venta) if self.precio_venta else 0,
            'imagen_url': self.imagen_url,
            'disponible_shopify': self.disponible_shopify,
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
    insumo_tipo = db.Column(db.Enum('Flor', 'Contenedor', name='insumo_tipo_enum'), nullable=False)
    insumo_id = db.Column(db.String(10), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    unidad = db.Column(db.String(20), nullable=False)
    es_opcional = db.Column(db.Boolean, default=False)
    notas = db.Column(db.Text)
    
    def to_dict(self):
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'insumo_tipo': self.insumo_tipo,
            'insumo_id': self.insumo_id,
            'cantidad': self.cantidad,
            'unidad': self.unidad,
            'es_opcional': self.es_opcional,
            'notas': self.notas
        }

