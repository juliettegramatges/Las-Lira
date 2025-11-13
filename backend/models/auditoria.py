"""
Modelo de Auditoría
Registra todas las acciones de los usuarios en el sistema
"""

from datetime import datetime
from extensions import db


class Auditoria(db.Model):
    """Tabla para registrar acciones de usuarios"""
    __tablename__ = 'auditoria'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    usuario_nombre = db.Column(db.String(100), nullable=False)  # Cache del nombre para historial
    accion = db.Column(db.String(100), nullable=False)  # 'crear', 'actualizar', 'eliminar', 'cambiar_estado', etc.
    entidad = db.Column(db.String(50), nullable=False)  # 'pedido', 'cliente', 'producto', 'cobranza', etc.
    entidad_id = db.Column(db.String(50))  # ID de la entidad afectada
    detalles = db.Column(db.Text)  # JSON string con detalles adicionales
    ip_address = db.Column(db.String(50))  # IP del usuario
    user_agent = db.Column(db.String(500))  # User agent del navegador
    fecha_accion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relación con usuario
    usuario = db.relationship('Usuario', backref='acciones', lazy=True)
    
    def to_dict(self):
        """Convierte el registro de auditoría a diccionario"""
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'usuario_nombre': self.usuario_nombre,
            'accion': self.accion,
            'entidad': self.entidad,
            'entidad_id': self.entidad_id,
            'detalles': self.detalles,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'fecha_accion': self.fecha_accion.isoformat() if self.fecha_accion else None
        }
    
    def __repr__(self):
        return f'<Auditoria {self.id}: {self.usuario_nombre} - {self.accion} {self.entidad}>'

