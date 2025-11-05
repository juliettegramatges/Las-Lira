#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplificado para recrear e importar inventario
"""

import sys
from pathlib import Path
import csv

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db

print("=" * 80)
print("🔄 RECREANDO INVENTARIO")
print("=" * 80)

with app.app_context():
    print("\n⚠️  PASO 1: Recreando TODAS las tablas...")
    print("   (Esto eliminará y recreará toda la base de datos)")
    
    db.drop_all()
    print("   ✅ Tablas eliminadas")
    
    db.create_all()
    print("   ✅ Tablas creadas con estructura actualizada")
    
    print("\n📦 PASO 2: Importando insumos desde CSV...")
    
    # Ahora importar los modelos después de crear las tablas
    from models.inventario import Flor, Contenedor
    
    csv_path = Path(backend_dir.parent) / 'insumos_las_lira.csv'
    
    if not csv_path.exists():
        print(f"   ❌ No se encontró: {csv_path}")
        sys.exit(1)
    
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
                    
                    flor = Flor(
                        id=f'F{siguiente_id_flor:04d}',
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
                
                else:
                    contenedor = Contenedor(
                        id=f'C{siguiente_id_contenedor:04d}',
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
            
            except Exception as e:
                print(f"   ❌ {nombre}: {e}")
    
    db.session.commit()
    
    print("\n" + "=" * 80)
    print("✅ COMPLETADO")
    print("=" * 80)
    print(f"\n   • Flores: {flores_creadas}")
    print(f"   • Contenedores: {contenedores_creados}")
    print("\n💡 Recarga el navegador y ve a 'Inventario'")
    print("=" * 80)


