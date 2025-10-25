#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar productos directamente con SQL
"""

import sys
from pathlib import Path
import csv
import sqlite3

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

print("=" * 80)
print("🎨 IMPORTANDO PRODUCTOS DIRECTAMENTE")
print("=" * 80)

# Rutas
db_path = backend_dir / 'instance' / 'laslira.db'
csv_dir = backend_dir.parent
catalogo_files = list(csv_dir.glob('catalogo_productos_completo*.csv'))

if not catalogo_files:
    print(f"❌ No se encontró el catálogo en: {csv_dir}")
    sys.exit(1)

if not db_path.exists():
    print(f"❌ No se encontró la base de datos: {db_path}")
    sys.exit(1)

# Tomar el archivo más reciente
csv_path = max(catalogo_files, key=lambda p: p.stat().st_mtime)

print(f"\n📄 Leyendo: {csv_path.name}")
print(f"💾 Base de datos: {db_path}")

# Conectar con SQLite
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("\n📋 Verificando tabla productos...")

# Verificar si la tabla existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos'")
if not cursor.fetchone():
    print("   ⚠️  Tabla productos no existe, creándola...")
    cursor.execute("""
        CREATE TABLE productos (
            id VARCHAR(10) PRIMARY KEY,
            nombre VARCHAR(200) NOT NULL,
            descripcion TEXT,
            tipo_arreglo VARCHAR(50),
            colores_asociados TEXT,
            flores_asociadas TEXT,
            tipos_macetero TEXT,
            vista_360_180 VARCHAR(50),
            tamano VARCHAR(100),
            precio_venta NUMERIC(10, 2),
            cuidados TEXT,
            imagen_url VARCHAR(500),
            disponible_shopify BOOLEAN DEFAULT 1
        )
    """)
    conn.commit()
    print("   ✅ Tabla creada")
else:
    print("   ✅ Tabla existe")

print("\n📦 Importando productos...")

productos_creados = 0
productos_actualizados = 0
errores = 0

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    
    for idx, row in enumerate(reader, start=1):
        try:
            nombre = row.get('Nombre del producto', row.get('Nombre', '')).strip()
            
            if not nombre:
                continue
            
            tipo_producto = row.get('Tipo de producto', '').strip()
            categoria = row.get('Categoría', '').strip()
            florero = row.get('Florero', '').strip()
            contenedor = row.get('Contenedor', '').strip()
            material = row.get('Material del contenedor', '').strip()
            colores = row.get('Colores', '').strip()
            flores_follajes = row.get('Insumos', row.get('Flores y/o Follajes', '')).strip()
            
            variantes_tamanos = row.get('Variantes_Tamaños', '').strip()
            dimensiones_tamanos = row.get('Dimensiones_Tamaños', '').strip()
            variantes_ruedo = row.get('Variantes_Ruedo', '').strip()
            variantes_colores = row.get('Variantes_Colores', '').strip()
            
            # Precios
            precio_base = row.get('precio_base', row.get('Precio', '')).strip()
            precio_s = row.get('Precio S', '').strip()
            precio_m = row.get('Precio M', '').strip()
            
            # Limpiar precios
            def limpiar_precio(p):
                if not p or p.lower() == 'variable':
                    return 0
                p = p.replace('$', '').replace('.', '').replace(',', '').strip()
                try:
                    return int(p)
                except:
                    return 0
            
            precio_venta = limpiar_precio(precio_base if precio_base else (precio_s if precio_s else precio_m))
            
            cuidados = row.get('Cuidados', '').strip()
            
            # Determinar tipo de arreglo
            if contenedor:
                if 'florero' in contenedor.lower() or 'vidrio' in contenedor.lower():
                    tipo_arreglo = 'Con Florero'
                elif 'macetero' in contenedor.lower() or 'maceta' in contenedor.lower():
                    tipo_arreglo = 'Con Macetero'
                elif 'canasto' in contenedor.lower():
                    tipo_arreglo = 'Con Canasto'
                elif 'caja' in contenedor.lower() or 'box' in contenedor.lower():
                    tipo_arreglo = 'Con Caja'
                elif 'papel' in contenedor.lower() or 'ramo' in tipo_producto.lower():
                    tipo_arreglo = 'Sin Contenedor'
                else:
                    tipo_arreglo = 'Con Contenedor'
            else:
                tipo_arreglo = 'Sin Contenedor'
            
            # Descripción
            descripcion_parts = []
            if tipo_producto:
                descripcion_parts.append(tipo_producto)
            if flores_follajes:
                descripcion_parts.append(f"Flores: {flores_follajes}")
            if contenedor and contenedor.lower() != 'sin florero (ramo)':
                descripcion_parts.append(f"Contenedor: {contenedor}")
            
            descripcion = '. '.join(descripcion_parts) if descripcion_parts else nombre
            
            # Verificar si existe
            cursor.execute("SELECT id FROM productos WHERE nombre = ?", (nombre,))
            existente = cursor.fetchone()
            
            if existente:
                # Actualizar
                cursor.execute("""
                    UPDATE productos SET
                        descripcion = ?,
                        tipo_arreglo = ?,
                        colores_asociados = ?,
                        flores_asociadas = ?,
                        tipos_macetero = ?,
                        vista_360_180 = ?,
                        tamano = ?,
                        precio_venta = ?,
                        cuidados = ?,
                        disponible_shopify = 1
                    WHERE nombre = ?
                """, (descripcion, tipo_arreglo, colores or variantes_colores, flores_follajes, 
                      contenedor, variantes_ruedo, variantes_tamanos or dimensiones_tamanos, 
                      precio_venta, cuidados, nombre))
                
                productos_actualizados += 1
                if productos_actualizados <= 5:
                    print(f"   🔄 Actualizado: {nombre}")
            else:
                # Crear
                producto_id = f'PR{idx:04d}'
                cursor.execute("""
                    INSERT INTO productos (id, nombre, descripcion, tipo_arreglo, colores_asociados,
                                          flores_asociadas, tipos_macetero, vista_360_180, tamano,
                                          precio_venta, cuidados, disponible_shopify)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                """, (producto_id, nombre, descripcion, tipo_arreglo, colores or variantes_colores,
                      flores_follajes, contenedor, variantes_ruedo, 
                      variantes_tamanos or dimensiones_tamanos, precio_venta, cuidados))
                
                productos_creados += 1
                if productos_creados <= 5 or productos_creados % 20 == 0:
                    print(f"   ✨ Producto {productos_creados}: {nombre}")
        
        except Exception as e:
            print(f"   ❌ Fila {idx} ({nombre}): {e}")
            errores += 1

conn.commit()

# Contar total
cursor.execute("SELECT COUNT(*) FROM productos")
total_productos = cursor.fetchone()[0]

conn.close()

print("\n" + "=" * 80)
print("✅ IMPORTACIÓN COMPLETADA")
print("=" * 80)
print(f"\n📊 Resumen:")
print(f"   • Productos creados: {productos_creados}")
print(f"   • Productos actualizados: {productos_actualizados}")
print(f"   • Errores: {errores}")
print(f"   • Total productos en DB: {total_productos}")

print("\n💡 Ahora:")
print("   1. Reinicia el backend (Ctrl+C y python3 app.py)")
print("   2. Recarga el navegador")
print("   3. Ve a 'Productos'")
print("=" * 80)

