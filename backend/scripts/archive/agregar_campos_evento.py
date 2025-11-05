"""
Script para agregar campos de evento a la tabla de pedidos
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db
from app import app

def agregar_campos_evento():
    """Agregar columnas es_evento y tipo_evento a la tabla pedidos"""
    with app.app_context():
        try:
            # Agregar columna es_evento
            db.session.execute(db.text("""
                ALTER TABLE pedidos 
                ADD COLUMN es_evento BOOLEAN DEFAULT 0
            """))
            print("✓ Columna 'es_evento' agregada")
            
            # Agregar columna tipo_evento
            db.session.execute(db.text("""
                ALTER TABLE pedidos 
                ADD COLUMN tipo_evento VARCHAR(50)
            """))
            print("✓ Columna 'tipo_evento' agregada")
            
            db.session.commit()
            print("\n✅ Migración completada exitosamente")
            
        except Exception as e:
            db.session.rollback()
            if "duplicate column name" in str(e).lower():
                print("⚠️  Las columnas ya existen")
            else:
                print(f"❌ Error: {e}")

if __name__ == '__main__':
    agregar_campos_evento()

