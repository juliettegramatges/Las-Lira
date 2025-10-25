#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar insumos desde CSV (insumos_las_lira.csv)
"""

import sys
import csv
from pathlib import Path

# Agregar el directorio backend al path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db
from models.inventario import Flor, Contenedor

print("=" * 80)
print("🌸 IMPORTANDO INSUMOS DESDE CSV")
print("=" * 80)

with app.app_context():
    # Leer el CSV de insumos
    csv_path = Path(__file__).parent.parent / 'insumos_las_lira.csv'
    
    if not csv_path.exists():
        print(f"❌ No se encontró el archivo: {csv_path}")
        sys.exit(1)
    
    print(f"\n📄 Leyendo: {csv_path}")
    
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
                                         'Azul', 'Azules', 'Verde', 'Verdes', 'Lila', 'Lilas']:
                        if color_posible in nombre:
                            color = color_posible
                            tipo_flor = nombre.replace(color_posible, '').strip()
                            break
                    
                    # Verificar si ya existe por nombre
                    existe = db.session.query(Flor).filter(
                        (Flor.nombre == nombre) | 
                        ((Flor.tipo == tipo_flor) & (Flor.color == color))
                    ).first()
                    
                    if not existe:
                        flor_id = f'F{siguiente_id_flor:04d}'
                        flor = Flor(
                            id=flor_id,
                            nombre=nombre,
                            tipo=tipo_flor,
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
                        print(f"   ✅ Flor: {nombre}")
                
                elif tipo_insumo in ['Contenedor', 'Macetero', 'Florero', 'Canasto', 'Caja', 
                                    'Jardinera', 'Copa', 'Ánfora', 'Base Metálica']:
                    # Es un contenedor
                    existe = Contenedor.query.filter_by(nombre=nombre).first()
                    
                    if not existe:
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
                        print(f"   ✅ Contenedor: {nombre}")
            
            except Exception as e:
                print(f"   ❌ Error en: {row.get('nombre', 'desconocido')} - {str(e)}")
                errores += 1
    
    # Guardar todos los cambios
    db.session.commit()
    
    print("\n" + "=" * 80)
    print("✅ IMPORTACIÓN COMPLETADA")
    print("=" * 80)
    print(f"\n📊 Resumen:")
    print(f"   • Flores creadas: {flores_creadas}")
    print(f"   • Contenedores creados: {contenedores_creados}")
    print(f"   • Errores: {errores}")
    print(f"   • Total flores en DB: {Flor.query.count()}")
    print(f"   • Total contenedores en DB: {Contenedor.query.count()}")
    print("\n💡 Recarga la página de Inventario en el navegador para verlos")
    print("=" * 80)

