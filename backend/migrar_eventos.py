"""
Script simple para agregar columnas de evento
"""
import sqlite3
import os

# Ruta a la base de datos
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'laslira.db')

print(f"Conectando a base de datos: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Intentar agregar columna es_evento
    try:
        cursor.execute("ALTER TABLE pedidos ADD COLUMN es_evento INTEGER DEFAULT 0")
        print("✓ Columna 'es_evento' agregada")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("⚠️  Columna 'es_evento' ya existe")
        else:
            raise
    
    # Intentar agregar columna tipo_evento
    try:
        cursor.execute("ALTER TABLE pedidos ADD COLUMN tipo_evento VARCHAR(50)")
        print("✓ Columna 'tipo_evento' agregada")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("⚠️  Columna 'tipo_evento' ya existe")
        else:
            raise
    
    conn.commit()
    print("\n✅ Migración completada exitosamente")
    
except Exception as e:
    print(f"❌ Error: {e}")
    if conn:
        conn.rollback()
finally:
    if conn:
        conn.close()
        print("🔒 Conexión cerrada")
