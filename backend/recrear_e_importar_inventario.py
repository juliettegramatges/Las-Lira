#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para recrear tablas de inventario e importar insumos desde CSV
"""

import sys
from pathlib import Path
import csv
from datetime import date

# Agregar el directorio backend al path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db
from models.inventario import Flor, Contenedor, Bodega

print("=" * 80)
print("🔄 RECREANDO INVENTARIO E IMPORTANDO INSUMOS")
print("=" * 80)

with app.app_context():
    print("\n⚠️  PASO 1: Eliminando tablas de inventario...")
    
    # Eliminar solo las tablas de inventario (no todos los datos)
    try:
        db.session.execute(db.text("DROP TABLE IF EXISTS flores"))
        db.session.execute(db.text("DROP TABLE IF EXISTS contenedores"))
        db.session.commit()
        print("   ✅ Tablas eliminadas")
    except Exception as e:
        print(f"   ⚠️  Error eliminando tablas: {e}")
    
    print("\n📋 PASO 2: Recreando tablas con estructura actualizada...")
    
    # Crear solo las tablas de inventario
    Flor.__table__.create(db.engine, checkfirst=True)
    Contenedor.__table__.create(db.engine, checkfirst=True)
    print("   ✅ Tablas creadas")
    
    print("\n📦 PASO 3: Importando insumos desde CSV...")
    
    csv_path = Path(backend_dir.parent) / 'insumos_las_lira.csv'
    
    if not csv_path.exists():
        print(f"   ❌ No se encontró el archivo: {csv_path}")
        sys.exit(1)
    
    print(f"   📄 Leyendo: {csv_path}")
    
    flores_creadas = 0
    contenedores_creados = 0
    errores = 0
    
    # Obtener el siguiente ID disponible
    ultimo_id_flor = db.session.query(db.func.max(Flor.id)).scalar() or 'F0000'
    siguiente_id_flor = int(ultimo_id_flor[1:]) + 1 if ultimo_id_flor.startswith('F') else 1
    
    ultimo_id_contenedor = db.session.query(db.func.max(Contenedor.id)).scalar() or 'C0000'
    siguiente_id_contenedor = int(ultimo_id_contenedor[1:]) + 1 if ultimo_id_contenedor.startswith('C') else 1
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                tipo_insumo = row['tipo_insumo']
                nombre = row['nombre']
                ubicacion = row['ubicacion']
                
                if tipo_insumo == 'Flor':
                    # Extraer color del nombre si existe
                    color = None
                    tipo_flor = nombre
                    
                    # Intentar separar tipo y color
                    for color_posible in ['Roja', 'Rojas', 'Blanca', 'Blancas', 'Rosada', 'Rosadas', 
                                         'Amarilla', 'Amarillas', 'Naranja', 'Naranjas', 'Morada', 'Moradas',
                                         'Azul', 'Azules', 'Verde', 'Verdes', 'Lila', 'Lilas', 'Amarillo', 'Amarillos']:
                        if color_posible in nombre:
                            color = color_posible
                            tipo_flor = nombre.replace(color_posible, '').strip()
                            break
                    
                    flor_id = f'F{siguiente_id_flor:04d}'
                    flor = Flor(
                        id=flor_id,
                        nombre=nombre,
                        tipo=tipo_flor or nombre,
                        color=color,
                        ubicacion=ubicacion,
                        cantidad_stock=0,
                        cantidad_en_uso=0,
                        cantidad_en_evento=0,
                        costo_unitario=0
                    )
                    db.session.add(flor)
                    flores_creadas += 1
                    siguiente_id_flor += 1
                    if flores_creadas <= 10 or flores_creadas % 10 == 0:
                        print(f"   🌸 Flor {flores_creadas}: {nombre}")
                
                elif tipo_insumo in ['Contenedor', 'Macetero', 'Florero', 'Canasto', 'Caja', 
                                    'Jardinera', 'Copa', 'Ánfora', 'Base Metálica']:
                    contenedor_id = f'C{siguiente_id_contenedor:04d}'
                    contenedor = Contenedor(
                        id=contenedor_id,
                        nombre=nombre,
                        tipo=tipo_insumo,
                        ubicacion=ubicacion,
                        cantidad_stock=0,
                        cantidad_en_uso=0,
                        cantidad_en_evento=0,
                        costo=0
                    )
                    db.session.add(contenedor)
                    contenedores_creados += 1
                    siguiente_id_contenedor += 1
                    if contenedores_creados <= 10 or contenedores_creados % 10 == 0:
                        print(f"   📦 Contenedor {contenedores_creados}: {nombre}")
            
            except Exception as e:
                print(f"   ❌ Error en: {row.get('nombre', 'desconocido')} - {str(e)}")
                errores += 1
    
    # Guardar todos los cambios
    try:
        db.session.commit()
        print("\n   ✅ Cambios guardados en la base de datos")
    except Exception as e:
        print(f"\n   ❌ Error al guardar: {e}")
        db.session.rollback()
    
    print("\n" + "=" * 80)
    print("✅ PROCESO COMPLETADO")
    print("=" * 80)
    print(f"\n📊 Resumen:")
    print(f"   • Flores creadas: {flores_creadas}")
    print(f"   • Contenedores creados: {contenedores_creados}")
    print(f"   • Errores: {errores}")
    
    # Verificar conteos finales
    total_flores = db.session.query(Flor).count()
    total_contenedores = db.session.query(Contenedor).count()
    print(f"\n   • Total flores en DB: {total_flores}")
    print(f"   • Total contenedores en DB: {total_contenedores}")
    
    print("\n💡 Recarga la página de Inventario en el navegador para verlos")
    print("=" * 80)

