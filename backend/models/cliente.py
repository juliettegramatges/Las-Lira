"""
Modelo de Cliente para gestión de base de datos de clientes
"""

from extensions import db
from datetime import datetime

class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.String(10), primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    telefono = db.Column(db.String(20))  # Sin unique ni nullable - datos históricos tienen duplicados
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
    
    def obtener_etiquetas(self):
        """Obtiene las etiquetas del cliente"""
        try:
            result = db.session.execute(db.text('''
                SELECT e.id, e.nombre, e.categoria, e.color, e.icono, e.descripcion
                FROM etiquetas_cliente e
                JOIN cliente_etiquetas ce ON ce.etiqueta_id = e.id
                WHERE ce.cliente_id = :cliente_id AND e.activa = 1
                ORDER BY e.orden
            '''), {'cliente_id': self.id})
            
            etiquetas = []
            for row in result:
                etiquetas.append({
                    'id': row[0],
                    'nombre': row[1],
                    'categoria': row[2],
                    'color': row[3],
                    'icono': row[4],
                    'descripcion': row[5]
                })
            return etiquetas
        except Exception as e:
            print(f"Error obteniendo etiquetas para cliente {self.id}: {e}")
            return []
    
    def to_dict(self, incluir_etiquetas=True):
        data = {
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
        
        if incluir_etiquetas:
            data['etiquetas'] = self.obtener_etiquetas()
        
        return data

