"""
Modelos para el sistema detallado de colores y flores por producto
"""

from datetime import datetime
from backend.app import db

class ProductoColor(db.Model):
    """
    Define los colores específicos que componen cada producto/arreglo.
    Ejemplo: "Pasión Roja" tiene colores: Rojo (12 flores), Verde oscuro (5 flores)
    """
    __tablename__ = 'producto_colores'
    
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.String(10), db.ForeignKey('productos.id'), nullable=False)
    nombre_color = db.Column(db.String(50), nullable=False)  # "Rojo", "Blanco", "Verde oscuro"
    cantidad_flores_sugerida = db.Column(db.Integer, default=0)  # Cantidad sugerida de flores
    orden = db.Column(db.Integer, default=0)  # Para ordenar visualmente los colores
    notas = db.Column(db.Text)  # Notas adicionales
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    producto = db.relationship('Producto', backref='colores')
    flores_disponibles = db.relationship('ProductoColorFlor', backref='color', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'nombre_color': self.nombre_color,
            'cantidad_flores_sugerida': self.cantidad_flores_sugerida,
            'orden': self.orden,
            'notas': self.notas,
            'activo': self.activo,
            'flores_disponibles': [f.to_dict() for f in self.flores_disponibles if f.activo]
        }
    
    def __repr__(self):
        return f'<ProductoColor {self.producto_id} - {self.nombre_color}>'


class ProductoColorFlor(db.Model):
    """
    Define qué flores están disponibles para cada color de cada producto.
    Ejemplo: Color "Rojo" del producto "Pasión Roja" puede usar: Rosa roja, Clavel rojo, Gerbera roja
    """
    __tablename__ = 'producto_color_flores'
    
    id = db.Column(db.Integer, primary_key=True)
    producto_color_id = db.Column(db.Integer, db.ForeignKey('producto_colores.id'), nullable=False)
    flor_id = db.Column(db.String(10), db.ForeignKey('flores.id'), nullable=False)
    es_predeterminada = db.Column(db.Boolean, default=False)  # La que se usa por defecto
    notas = db.Column(db.Text)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    flor = db.relationship('Flor', backref='productos_colores')
    
    def to_dict(self):
        return {
            'id': self.id,
            'producto_color_id': self.producto_color_id,
            'flor_id': self.flor_id,
            'flor_nombre': f"{self.flor.tipo} {self.flor.color}" if self.flor else None,
            'flor_costo': float(self.flor.costo_unitario) if self.flor else 0,
            'flor_stock': self.flor.cantidad_stock if self.flor else 0,
            'flor_unidad': self.flor.unidad if self.flor else 'tallo',
            'es_predeterminada': self.es_predeterminada,
            'notas': self.notas,
            'activo': self.activo
        }
    
    def __repr__(self):
        return f'<ProductoColorFlor {self.producto_color_id} - {self.flor_id}>'


class PedidoFlorSeleccionada(db.Model):
    """
    Guarda las flores específicas seleccionadas en cada pedido.
    Permite trazabilidad exacta de qué flores se usaron en cada arreglo.
    """
    __tablename__ = 'pedido_flores_seleccionadas'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.String(20), db.ForeignKey('pedidos.id'), nullable=False)
    producto_color_id = db.Column(db.Integer, db.ForeignKey('producto_colores.id'))  # Puede ser null para pedidos personalizados
    color_nombre = db.Column(db.String(50))  # Para referencia rápida
    flor_id = db.Column(db.String(10), db.ForeignKey('flores.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    costo_unitario = db.Column(db.Numeric(10, 2), nullable=False)  # Costo al momento del pedido
    costo_total = db.Column(db.Numeric(10, 2), nullable=False)  # cantidad * costo_unitario
    descontado_stock = db.Column(db.Boolean, default=False)  # Si ya se descontó del inventario
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    pedido = db.relationship('Pedido', backref='flores_seleccionadas')
    flor = db.relationship('Flor')
    producto_color = db.relationship('ProductoColor')
    
    def to_dict(self):
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'color_nombre': self.color_nombre,
            'flor_id': self.flor_id,
            'flor_nombre': f"{self.flor.tipo} {self.flor.color}" if self.flor else None,
            'cantidad': self.cantidad,
            'costo_unitario': float(self.costo_unitario),
            'costo_total': float(self.costo_total),
            'descontado_stock': self.descontado_stock,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }
    
    def __repr__(self):
        return f'<PedidoFlorSeleccionada {self.pedido_id} - {self.flor_id} x{self.cantidad}>'


class PedidoContenedorSeleccionado(db.Model):
    """
    Guarda los contenedores específicos seleccionados en cada pedido.
    Similar a PedidoFlorSeleccionada pero para contenedores.
    """
    __tablename__ = 'pedido_contenedores_seleccionados'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.String(20), db.ForeignKey('pedidos.id'), nullable=False)
    contenedor_id = db.Column(db.String(10), db.ForeignKey('contenedores.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    costo_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    costo_total = db.Column(db.Numeric(10, 2), nullable=False)
    descontado_stock = db.Column(db.Boolean, default=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    pedido = db.relationship('Pedido', backref='contenedores_seleccionados')
    contenedor = db.relationship('Contenedor')
    
    def to_dict(self):
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'contenedor_id': self.contenedor_id,
            'contenedor_nombre': f"{self.contenedor.tipo} {self.contenedor.material}" if self.contenedor else None,
            'cantidad': self.cantidad,
            'costo_unitario': float(self.costo_unitario),
            'costo_total': float(self.costo_total),
            'descontado_stock': self.descontado_stock,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }
    
    def __repr__(self):
        return f'<PedidoContenedorSeleccionado {self.pedido_id} - {self.contenedor_id}>'

