"""
Modelo de Usuario para autenticación y control de acceso
"""
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='taller')  # admin, secretaria, taller
    nombre = db.Column(db.String(100), nullable=False)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ultimo_acceso = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        """Genera el hash de la contraseña"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convierte el usuario a diccionario (sin password)"""
        return {
            'id': self.id,
            'username': self.username,
            'rol': self.rol,
            'nombre': self.nombre,
            'activo': self.activo,
            'fecha_creacion': self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            'ultimo_acceso': self.ultimo_acceso.isoformat() if self.ultimo_acceso else None
        }
    
    def __repr__(self):
        return f'<Usuario {self.username} ({self.rol})>'

