"""
Modelos para gestión de eventos
"""

from extensions import db
from datetime import datetime
from sqlalchemy import Numeric


class Evento(db.Model):
    """Modelo para eventos"""
    __tablename__ = 'eventos'
    
    id = db.Column(db.String(20), primary_key=True)
    
    # Información del Cliente
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    cliente_nombre = db.Column(db.String(200))
    cliente_telefono = db.Column(db.String(50))
    cliente_email = db.Column(db.String(200))
    
    # Información del Evento
    nombre_evento = db.Column(db.String(200))
    tipo_evento = db.Column(db.String(100))  # Boda, Cumpleaños, Corporativo, etc.
    fecha_evento = db.Column(db.DateTime)
    hora_evento = db.Column(db.String(20))
    lugar_evento = db.Column(db.String(500))
    cantidad_personas = db.Column(db.Integer)
    
    # Estado del Evento
    estado = db.Column(db.String(50), default='Cotización')
    # Estados: Cotización, Propuesta Enviada, Confirmado, En Preparación, En Evento, Finalizado, Retirado
    
    # Costos
    costo_insumos = db.Column(Numeric(10, 2), default=0)
    costo_mano_obra = db.Column(Numeric(10, 2), default=0)
    costo_transporte = db.Column(Numeric(10, 2), default=0)
    costo_otros = db.Column(Numeric(10, 2), default=0)
    costo_total = db.Column(Numeric(10, 2), default=0)
    
    # Precio y Margen
    margen_porcentaje = db.Column(Numeric(5, 2), default=30)  # % de margen deseado
    precio_propuesta = db.Column(Numeric(10, 2), default=0)
    precio_final = db.Column(Numeric(10, 2), default=0)
    
    # Pago
    anticipo = db.Column(Numeric(10, 2), default=0)
    saldo = db.Column(Numeric(10, 2), default=0)
    pagado = db.Column(db.Boolean, default=False)
    
    # Insumos
    insumos_reservados = db.Column(db.Boolean, default=False)
    insumos_descontados = db.Column(db.Boolean, default=False)
    insumos_faltantes = db.Column(db.Boolean, default=False)
    lista_faltantes = db.Column(db.Text)  # JSON con insumos faltantes
    
    # Notas
    notas_cotizacion = db.Column(db.Text)
    notas_internas = db.Column(db.Text)
    notas_faltantes = db.Column(db.Text)
    
    # Fechas de control
    fecha_cotizacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_propuesta = db.Column(db.DateTime)
    fecha_confirmacion = db.Column(db.DateTime)
    fecha_finalizacion = db.Column(db.DateTime)
    fecha_retiro = db.Column(db.DateTime)
    
    # Relaciones
    insumos = db.relationship('EventoInsumo', backref='evento', lazy=True, cascade='all, delete-orphan')
    cliente = db.relationship('Cliente', backref='eventos', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_nombre': self.cliente_nombre,
            'cliente_telefono': self.cliente_telefono,
            'cliente_email': self.cliente_email,
            'nombre_evento': self.nombre_evento,
            'tipo_evento': self.tipo_evento,
            'fecha_evento': self.fecha_evento.isoformat() if self.fecha_evento else None,
            'hora_evento': self.hora_evento,
            'lugar_evento': self.lugar_evento,
            'cantidad_personas': self.cantidad_personas,
            'estado': self.estado,
            'costo_insumos': float(self.costo_insumos) if self.costo_insumos else 0,
            'costo_mano_obra': float(self.costo_mano_obra) if self.costo_mano_obra else 0,
            'costo_transporte': float(self.costo_transporte) if self.costo_transporte else 0,
            'costo_otros': float(self.costo_otros) if self.costo_otros else 0,
            'costo_total': float(self.costo_total) if self.costo_total else 0,
            'margen_porcentaje': float(self.margen_porcentaje) if self.margen_porcentaje else 0,
            'precio_propuesta': float(self.precio_propuesta) if self.precio_propuesta else 0,
            'precio_final': float(self.precio_final) if self.precio_final else 0,
            'anticipo': float(self.anticipo) if self.anticipo else 0,
            'saldo': float(self.saldo) if self.saldo else 0,
            'pagado': self.pagado,
            'insumos_reservados': self.insumos_reservados,
            'insumos_descontados': self.insumos_descontados,
            'insumos_faltantes': self.insumos_faltantes,
            'lista_faltantes': self.lista_faltantes,
            'notas_cotizacion': self.notas_cotizacion,
            'notas_internas': self.notas_internas,
            'notas_faltantes': self.notas_faltantes,
            'fecha_cotizacion': self.fecha_cotizacion.isoformat() if self.fecha_cotizacion else None,
            'fecha_propuesta': self.fecha_propuesta.isoformat() if self.fecha_propuesta else None,
            'fecha_confirmacion': self.fecha_confirmacion.isoformat() if self.fecha_confirmacion else None,
            'fecha_finalizacion': self.fecha_finalizacion.isoformat() if self.fecha_finalizacion else None,
            'fecha_retiro': self.fecha_retiro.isoformat() if self.fecha_retiro else None,
        }


class EventoInsumo(db.Model):
    """Modelo para insumos de eventos"""
    __tablename__ = 'evento_insumos'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    evento_id = db.Column(db.String(20), db.ForeignKey('eventos.id'), nullable=False)
    
    # Tipo de insumo
    tipo_insumo = db.Column(db.String(50))  # flor, contenedor, producto, producto_evento, otro
    
    # Referencias (solo una será válida según tipo_insumo)
    flor_id = db.Column(db.String(20), db.ForeignKey('flores.id'), nullable=True)
    contenedor_id = db.Column(db.String(20), db.ForeignKey('contenedores.id'), nullable=True)
    producto_id = db.Column(db.String(20), db.ForeignKey('productos.id'), nullable=True)
    producto_evento_id = db.Column(db.Integer, db.ForeignKey('productos_evento.id'), nullable=True)
    
    # Para insumos "otros" (velas, manteles, etc sin referencia)
    nombre_otro = db.Column(db.String(200))
    
    # Cantidad y costos
    cantidad = db.Column(db.Integer, default=1)
    costo_unitario = db.Column(Numeric(10, 2), default=0)
    costo_total = db.Column(Numeric(10, 2), default=0)
    
    # Control
    reservado = db.Column(db.Boolean, default=False)
    descontado_stock = db.Column(db.Boolean, default=False)
    devuelto = db.Column(db.Boolean, default=False)
    cantidad_faltante = db.Column(db.Integer, default=0)
    
    # Notas
    notas = db.Column(db.Text)
    
    # Relaciones
    flor = db.relationship('Flor', backref='eventos_uso', lazy=True)
    contenedor = db.relationship('Contenedor', backref='eventos_uso', lazy=True)
    producto = db.relationship('Producto', backref='eventos_uso', lazy=True)
    
    def to_dict(self):
        nombre = None
        stock_disponible = None
        
        if self.tipo_insumo == 'flor' and self.flor:
            nombre = self.flor.nombre
            stock_disponible = self.flor.cantidad_disponible
        elif self.tipo_insumo == 'contenedor' and self.contenedor:
            nombre = f"{self.contenedor.tipo} - {self.contenedor.nombre}"
            stock_disponible = self.contenedor.cantidad_disponible
        elif self.tipo_insumo == 'producto' and self.producto:
            nombre = self.producto.nombre
            stock_disponible = None  # Los productos no tienen stock directo
        elif self.tipo_insumo == 'otro':
            nombre = self.nombre_otro
            stock_disponible = None
        
        return {
            'id': self.id,
            'evento_id': self.evento_id,
            'tipo_insumo': self.tipo_insumo,
            'flor_id': self.flor_id,
            'contenedor_id': self.contenedor_id,
            'producto_id': self.producto_id,
            'nombre_otro': self.nombre_otro,
            'nombre': nombre,
            'cantidad': self.cantidad,
            'costo_unitario': float(self.costo_unitario) if self.costo_unitario else 0,
            'costo_total': float(self.costo_total) if self.costo_total else 0,
            'reservado': self.reservado,
            'descontado_stock': self.descontado_stock,
            'devuelto': self.devuelto,
            'cantidad_faltante': self.cantidad_faltante,
            'stock_disponible': stock_disponible,
            'notas': self.notas
        }


class ProductoEvento(db.Model):
    """Modelo para productos específicos de eventos (velas, manteles, triángulos, etc)"""
    __tablename__ = 'productos_evento'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    codigo = db.Column(db.String(20), unique=True)
    nombre = db.Column(db.String(200))
    categoria = db.Column(db.String(100))  # Decoración, Mobiliario, Iluminación, Mantelería, etc.
    
    # Cantidad disponible
    cantidad_stock = db.Column(db.Integer, default=0)
    cantidad_en_evento = db.Column(db.Integer, default=0)
    
    # Costos
    costo_compra = db.Column(Numeric(10, 2), default=0)
    costo_alquiler = db.Column(Numeric(10, 2), default=0)  # Si se alquila
    
    # Características
    descripcion = db.Column(db.Text)
    medidas = db.Column(db.String(200))
    color = db.Column(db.String(100))
    material = db.Column(db.String(100))
    
    # Control
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foto
    imagen_url = db.Column(db.String(500))
    
    @property
    def cantidad_disponible(self):
        return (self.cantidad_stock or 0) - (self.cantidad_en_evento or 0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'nombre': self.nombre,
            'categoria': self.categoria,
            'cantidad_stock': self.cantidad_stock or 0,
            'cantidad_en_evento': self.cantidad_en_evento or 0,
            'cantidad_disponible': self.cantidad_disponible,
            'costo_compra': float(self.costo_compra) if self.costo_compra else 0,
            'costo_alquiler': float(self.costo_alquiler) if self.costo_alquiler else 0,
            'descripcion': self.descripcion,
            'medidas': self.medidas,
            'color': self.color,
            'material': self.material,
            'activo': self.activo,
            'imagen_url': self.imagen_url
        }

