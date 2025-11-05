#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para agregar campos de personalización usando sqlite3
"""

import sqlite3
import os
from pathlib import Path

# Ruta de la base de datos
backend_dir = Path(__file__).resolve().parent
db_path = backend_dir / 'instance' / 'laslira.db'

print("=" * 80)
print("🎨 MEJORANDO SISTEMA DE PERSONALIZACIONES")
print("=" * 80)

if not db_path.exists():
    print(f"❌ ERROR: Base de datos no encontrada en {db_path}")
    exit(1)

print(f"\n📂 Conectando a: {db_path}")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # ========================================
    # 1. TABLA PRODUCTOS
    # ========================================
    print("\n📦 Mejorando tabla PRODUCTOS...")
    
    # Verificar columnas existentes
    cursor.execute("PRAGMA table_info(productos)")
    columnas_productos = [col[1] for col in cursor.fetchall()]
    
    # Agregar es_personalizacion
    if 'es_personalizacion' not in columnas_productos:
        cursor.execute('''
            ALTER TABLE productos 
            ADD COLUMN es_personalizacion BOOLEAN DEFAULT 0
        ''')
        conn.commit()
        print("   ✓ Columna 'es_personalizacion' agregada")
    else:
        print("   ℹ️  Columna 'es_personalizacion' ya existe")
    
    # Agregar categoria_personalizacion
    if 'categoria_personalizacion' not in columnas_productos:
        cursor.execute('''
            ALTER TABLE productos 
            ADD COLUMN categoria_personalizacion VARCHAR(100)
        ''')
        conn.commit()
        print("   ✓ Columna 'categoria_personalizacion' agregada")
    else:
        print("   ℹ️  Columna 'categoria_personalizacion' ya existe")
    
    # ========================================
    # 2. TABLA PEDIDOS
    # ========================================
    print("\n📝 Mejorando tabla PEDIDOS...")
    
    # Verificar columnas existentes
    cursor.execute("PRAGMA table_info(pedidos)")
    columnas_pedidos = [col[1] for col in cursor.fetchall()]
    
    # Agregar colores_solicitados
    if 'colores_solicitados' not in columnas_pedidos:
        cursor.execute('''
            ALTER TABLE pedidos 
            ADD COLUMN colores_solicitados TEXT
        ''')
        conn.commit()
        print("   ✓ Columna 'colores_solicitados' agregada")
    else:
        print("   ℹ️  Columna 'colores_solicitados' ya existe")
    
    # Agregar tipo_personalizacion
    if 'tipo_personalizacion' not in columnas_pedidos:
        cursor.execute('''
            ALTER TABLE pedidos 
            ADD COLUMN tipo_personalizacion VARCHAR(100)
        ''')
        conn.commit()
        print("   ✓ Columna 'tipo_personalizacion' agregada")
    else:
        print("   ℹ️  Columna 'tipo_personalizacion' ya existe")
    
    # Agregar notas_personalizacion
    if 'notas_personalizacion' not in columnas_pedidos:
        cursor.execute('''
            ALTER TABLE pedidos 
            ADD COLUMN notas_personalizacion TEXT
        ''')
        conn.commit()
        print("   ✓ Columna 'notas_personalizacion' agregada")
    else:
        print("   ℹ️  Columna 'notas_personalizacion' ya existe")
    
    # ========================================
    # 3. MARCAR PRODUCTO PERSONALIZACIÓN
    # ========================================
    print("\n🎨 Configurando producto 'Personalización'...")
    
    # Buscar producto "Personalización"
    cursor.execute('''
        SELECT id, nombre FROM productos 
        WHERE nombre LIKE '%Personalización%' OR nombre LIKE '%personaliz%'
    ''')
    productos_pers = cursor.fetchall()
    
    if productos_pers:
        for prod_id, nombre in productos_pers:
            cursor.execute('''
                UPDATE productos 
                SET es_personalizacion = 1,
                    categoria_personalizacion = 'General'
                WHERE id = ?
            ''', (prod_id,))
            conn.commit()
            print(f"   ✓ Producto '{nombre}' marcado como personalización (ID: {prod_id})")
    else:
        print("   ⚠️  No se encontró producto 'Personalización'")
        print("      Créalo con: python3 backend/scripts/agregar_personalizacion.py")
    
    # ========================================
    # 4. RESUMEN FINAL
    # ========================================
    print("\n" + "=" * 80)
    print("✅ MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 80)
    
    print("\n📊 NUEVOS CAMPOS AGREGADOS:\n")
    print("🎨 TABLA: productos")
    print("   • es_personalizacion (BOOLEAN)")
    print("   • categoria_personalizacion (VARCHAR)")
    
    print("\n📝 TABLA: pedidos")
    print("   • colores_solicitados (TEXT)")
    print("   • tipo_personalizacion (VARCHAR)")
    print("   • notas_personalizacion (TEXT)")
    
    print("\n" + "=" * 80)
    print("🚀 ENDPOINTS DISPONIBLES:")
    print("=" * 80)
    print("   GET  /api/analisis/personalizaciones")
    print("   GET  /api/analisis/personalizaciones/detalle?page=1&limit=50")
    
    print("\n" + "=" * 80)
    print("📖 DOCUMENTACIÓN COMPLETA:")
    print("=" * 80)
    print("   Lee: SISTEMA_PERSONALIZACIONES.md")
    
    conn.close()
    print("\n✅ Migración completada. Reinicia el backend.\n")
    
except sqlite3.Error as e:
    print(f"\n❌ ERROR SQL: {e}")
    if conn:
        conn.rollback()
        conn.close()
    exit(1)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    if conn:
        conn.rollback()
        conn.close()
    exit(1)

