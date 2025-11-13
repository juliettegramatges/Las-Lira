"""
Script para crear la tabla de auditoría
"""

import sqlite3
import os

# Obtener ruta de la base de datos
basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
db_path = os.path.join(basedir, 'instance', 'laslira.db')

if not os.path.exists(os.path.dirname(db_path)):
    os.makedirs(os.path.dirname(db_path))

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Verificar si la tabla ya existe
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name='auditoria'
""")

if cursor.fetchone():
    print("✅ La tabla 'auditoria' ya existe")
else:
    # Crear tabla de auditoría
    cursor.execute("""
        CREATE TABLE auditoria (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            usuario_nombre VARCHAR(100) NOT NULL,
            accion VARCHAR(100) NOT NULL,
            entidad VARCHAR(50) NOT NULL,
            entidad_id VARCHAR(50),
            detalles TEXT,
            ip_address VARCHAR(50),
            user_agent VARCHAR(500),
            fecha_accion DATETIME NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    """)
    
    # Crear índices para mejorar rendimiento
    cursor.execute("CREATE INDEX idx_auditoria_usuario ON auditoria(usuario_id)")
    cursor.execute("CREATE INDEX idx_auditoria_fecha ON auditoria(fecha_accion)")
    cursor.execute("CREATE INDEX idx_auditoria_entidad ON auditoria(entidad)")
    
    conn.commit()
    print("✅ Tabla 'auditoria' creada exitosamente")
    print("✅ Índices creados")

conn.close()
print("✅ Script completado")

