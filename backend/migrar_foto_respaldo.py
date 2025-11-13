"""
Migración: Agregar columna foto_respaldo a pedidos_productos
"""

import sqlite3
import os

# Obtener la ruta de la base de datos
backend_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(backend_dir, 'instance', 'laslira.db')

print(f"📁 Ruta de la base de datos: {db_path}")

# Verificar que existe
if not os.path.exists(db_path):
    print(f"❌ No se encuentra la base de datos en {db_path}")
    exit(1)

# Conectar
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Verificar si la columna ya existe
    cursor.execute("PRAGMA table_info(pedidos_productos)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'foto_respaldo' in columns:
        print("✅ La columna 'foto_respaldo' ya existe en pedidos_productos")
    else:
        print("➕ Agregando columna 'foto_respaldo' a pedidos_productos...")
        cursor.execute("ALTER TABLE pedidos_productos ADD COLUMN foto_respaldo VARCHAR(500)")
        conn.commit()
        print("✅ Columna 'foto_respaldo' agregada exitosamente")

    # Verificar la estructura final
    cursor.execute("PRAGMA table_info(pedidos_productos)")
    columns_info = cursor.fetchall()

    print(f"\n📋 Estructura de la tabla pedidos_productos:")
    for col in columns_info:
        print(f"   - {col[1]} ({col[2]})")

except Exception as e:
    print(f"❌ Error durante la migración: {str(e)}")
    conn.rollback()
finally:
    conn.close()
    print("\n🔒 Conexión cerrada")
