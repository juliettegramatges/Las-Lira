#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar inventario directamente (sin verificar si existe)
"""

import sys
from pathlib import Path
import csv
import sqlite3

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

print("=" * 80)
print("🔄 IMPORTANDO INVENTARIO DIRECTAMENTE")
print("=" * 80)

# Ruta a la base de datos
db_path = backend_dir / 'instance' / 'laslira.db'
csv_path = backend_dir.parent / 'insumos_las_lira.csv'

if not csv_path.exists():
    print(f"❌ No se encontró: {csv_path}")
    sys.exit(1)

if not db_path.exists():
    print(f"❌ No se encontró la base de datos: {db_path}")
    sys.exit(1)

print(f"\n📄 Leyendo: {csv_path}")
print(f"💾 Base de datos: {db_path}")

# Conectar directamente con SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n⚠️  PASO 1: Eliminando tablas de inventario existentes...")

try:
    cursor.execute("DROP TABLE IF EXISTS flores")
    cursor.execute("DROP TABLE IF EXISTS contenedores")
    conn.commit()
    print("   ✅ Tablas eliminadas")
except Exception as e:
    print(f"   ⚠️  Error: {e}")

print("\n📋 PASO 2: Creando nuevas tablas con estructura actualizada...")

# Crear tabla flores
cursor.execute("""
CREATE TABLE IF NOT EXISTS flores (
    id VARCHAR(10) PRIMARY KEY,
    tipo VARCHAR(50) NOT NULL,
    color VARCHAR(30),
    nombre VARCHAR(100),
    ubicacion VARCHAR(100),
    foto_url VARCHAR(500),
    proveedor_id VARCHAR(10),
    costo_unitario NUMERIC(10, 2) DEFAULT 0,
    cantidad_stock INTEGER DEFAULT 0 NOT NULL,
    cantidad_en_uso INTEGER DEFAULT 0 NOT NULL,
    cantidad_en_evento INTEGER DEFAULT 0 NOT NULL,
    unidad VARCHAR(20) DEFAULT 'Tallos',
    fecha_actualizacion DATE
)
""")

# Crear tabla contenedores
cursor.execute("""
CREATE TABLE IF NOT EXISTS contenedores (
    id VARCHAR(10) PRIMARY KEY,
    nombre VARCHAR(100),
    tipo VARCHAR(50),
    material VARCHAR(30),
    forma VARCHAR(30),
    tamano VARCHAR(50),
    color VARCHAR(30),
    ubicacion VARCHAR(100),
    foto_url VARCHAR(500),
    costo NUMERIC(10, 2) DEFAULT 0,
    cantidad_stock INTEGER DEFAULT 0 NOT NULL,
    cantidad_en_uso INTEGER DEFAULT 0 NOT NULL,
    cantidad_en_evento INTEGER DEFAULT 0 NOT NULL,
    stock INTEGER DEFAULT 0 NOT NULL,
    bodega_id INTEGER,
    fecha_actualizacion DATE
)
""")

conn.commit()
print("   ✅ Tablas creadas")

print("\n📦 PASO 3: Importando insumos...")

flores_creadas = 0
contenedores_creados = 0
siguiente_id_flor = 1
siguiente_id_contenedor = 1

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for row in reader:
        try:
            tipo_insumo = row['tipo_insumo']
            nombre = row['nombre']
            ubicacion = row['ubicacion']
            
            if tipo_insumo == 'Flor':
                color = None
                tipo_flor = nombre
                
                for color_posible in ['Roja', 'Rojas', 'Blanca', 'Blancas', 'Rosada', 'Rosadas', 
                                     'Amarilla', 'Amarillas', 'Naranja', 'Naranjas', 'Morada', 'Moradas',
                                     'Azul', 'Azules', 'Verde', 'Verdes', 'Lila', 'Lilas', 'Amarillo', 'Amarillos']:
                    if color_posible in nombre:
                        color = color_posible
                        tipo_flor = nombre.replace(color_posible, '').strip()
                        break
                
                flor_id = f'F{siguiente_id_flor:04d}'
                cursor.execute("""
                    INSERT INTO flores (id, nombre, tipo, color, ubicacion, cantidad_stock, 
                                       cantidad_en_uso, cantidad_en_evento, costo_unitario, unidad, fecha_actualizacion)
                    VALUES (?, ?, ?, ?, ?, 0, 0, 0, 0, 'Tallos', date('now'))
                """, (flor_id, nombre, tipo_flor or nombre, color, ubicacion))
                
                flores_creadas += 1
                siguiente_id_flor += 1
                
                if flores_creadas <= 5 or flores_creadas % 10 == 0:
                    print(f"   🌸 Flor {flores_creadas}: {nombre}")
            
            else:
                contenedor_id = f'C{siguiente_id_contenedor:04d}'
                cursor.execute("""
                    INSERT INTO contenedores (id, nombre, tipo, ubicacion, cantidad_stock, stock,
                                             cantidad_en_uso, cantidad_en_evento, costo, fecha_actualizacion)
                    VALUES (?, ?, ?, ?, 0, 0, 0, 0, 0, date('now'))
                """, (contenedor_id, nombre, tipo_insumo, ubicacion))
                
                contenedores_creados += 1
                siguiente_id_contenedor += 1
                
                if contenedores_creados <= 5 or contenedores_creados % 10 == 0:
                    print(f"   📦 Contenedor {contenedores_creados}: {nombre}")
        
        except Exception as e:
            print(f"   ❌ {nombre}: {e}")

conn.commit()
conn.close()

print("\n" + "=" * 80)
print("✅ IMPORTACIÓN COMPLETADA")
print("=" * 80)
print(f"\n📊 Resumen:")
print(f"   • Flores creadas: {flores_creadas}")
print(f"   • Contenedores creados: {contenedores_creados}")
print("\n💡 Ahora:")
print("   1. Reinicia el backend (Ctrl+C y python3 app.py)")
print("   2. Recarga el navegador")
print("   3. Ve a 'Inventario'")
print("=" * 80)

