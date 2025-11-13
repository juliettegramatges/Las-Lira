#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar insumos desde CSV (insumos_las_lira.csv)
"""

import sys
import csv
from pathlib import Path
from datetime import date

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
    # Buscar el CSV en el directorio raíz
    csv_path = backend_dir.parent / 'insumos_las_lira.csv'
    
    if not csv_path.exists():
        # Intentar con el otro nombre
        csv_path = backend_dir.parent / 'insumos_las_lira_v2_20251025_0621.csv'
    
    if not csv_path.exists():
        print(f"❌ No se encontró el archivo CSV en:")
        print(f"   • {backend_dir.parent / 'insumos_las_lira.csv'}")
        print(f"   • {backend_dir.parent / 'insumos_las_lira_v2_20251025_0621.csv'}")
        sys.exit(1)
    
    print(f"\n📄 Leyendo: {csv_path}")
    
    flores_creadas = 0
    contenedores_creados = 0
    flores_existentes = 0
    contenedores_existentes = 0
    errores = 0
    
    # Obtener el siguiente ID disponible
    ultimo_flor = Flor.query.order_by(Flor.id.desc()).first()
    if ultimo_flor and ultimo_flor.id.startswith('FL'):
        try:
            siguiente_id_flor = int(ultimo_flor.id[2:]) + 1
        except:
            siguiente_id_flor = Flor.query.count() + 1
    else:
        siguiente_id_flor = Flor.query.count() + 1
    
    ultimo_contenedor = Contenedor.query.order_by(Contenedor.id.desc()).first()
    if ultimo_contenedor and ultimo_contenedor.id.startswith('C'):
        try:
            siguiente_id_contenedor = int(ultimo_contenedor.id[1:]) + 1
        except:
            siguiente_id_contenedor = Contenedor.query.count() + 1
    else:
        siguiente_id_contenedor = Contenedor.query.count() + 1
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                tipo_insumo = row.get('tipo_insumo', '').strip()
                nombre = row.get('nombre', '').strip()
                ubicacion = row.get('ubicacion', 'Taller').strip() or 'Taller'
                
                if not nombre:
                    continue
                
                if tipo_insumo == 'Flor':
                    # Extraer color del nombre si existe
                    color = None
                    tipo_flor = nombre
                    
                    # Lista de colores posibles
                    colores_posibles = [
                        'Roja', 'Rojas', 'Rojo', 'Rojos',
                        'Blanca', 'Blancas', 'Blanco', 'Blancos',
                        'Rosada', 'Rosadas', 'Rosado', 'Rosados',
                        'Amarilla', 'Amarillas', 'Amarillo', 'Amarillos',
                        'Naranja', 'Naranjas', 'Naranjo', 'Naranjos',
                        'Morada', 'Moradas', 'Morado', 'Morados',
                        'Azul', 'Azules',
                        'Verde', 'Verdes',
                        'Lila', 'Lilas',
                        'Rosa', 'Rosas',
                        'Amarilla', 'Amarillas'
                    ]
                    
                    # Intentar separar tipo y color
                    for color_posible in colores_posibles:
                        if color_posible in nombre:
                            color = color_posible
                            tipo_flor = nombre.replace(color_posible, '').strip()
                            break
                    
                    # Normalizar color (Roja -> Rojo, Blancas -> Blanco, etc.)
                    if color:
                        if color.endswith('a') or color.endswith('as'):
                            color = color.rstrip('as').rstrip('a')
                        if color.endswith('os'):
                            color = color.rstrip('os')
                    
                    # Verificar si ya existe por nombre
                    existe = Flor.query.filter_by(nombre=nombre).first()
                    
                    if not existe:
                        flor_id = f'FL{str(siguiente_id_flor).zfill(3)}'
                        flor = Flor(
                            id=flor_id,
                            nombre=nombre,
                            tipo=tipo_flor or nombre,
                            color=color,
                            ubicacion=ubicacion,
                            cantidad_stock=0,
                            cantidad_en_uso=0,
                            cantidad_en_evento=0,
                            costo_unitario=0,
                            stock_bajo=10,  # Valor por defecto
                            unidad='Tallos',
                            fecha_actualizacion=date.today()
                        )
                        db.session.add(flor)
                        flores_creadas += 1
                        siguiente_id_flor += 1
                        if flores_creadas <= 10 or flores_creadas % 20 == 0:
                            print(f"   ✅ Flor {flores_creadas}: {nombre}")
                    else:
                        flores_existentes += 1
                
                elif tipo_insumo in ['Contenedor', 'Macetero', 'Florero', 'Canasto', 'Caja', 
                                    'Jardinera', 'Copa', 'Ánfora', 'Base Metálica', 'Vaso', 'Tarro']:
                    # Es un contenedor
                    existe = Contenedor.query.filter_by(nombre=nombre).first()
                    
                    if not existe:
                        contenedor_id = f'C{str(siguiente_id_contenedor).zfill(3)}'
                        contenedor = Contenedor(
                            id=contenedor_id,
                            nombre=nombre,
                            tipo=tipo_insumo,
                            ubicacion=ubicacion,
                            cantidad_stock=0,
                            cantidad_en_uso=0,
                            cantidad_en_evento=0,
                            costo=0,
                            stock_bajo=5,  # Valor por defecto
                            fecha_actualizacion=date.today()
                        )
                        db.session.add(contenedor)
                        contenedores_creados += 1
                        siguiente_id_contenedor += 1
                        if contenedores_creados <= 10 or contenedores_creados % 20 == 0:
                            print(f"   ✅ Contenedor {contenedores_creados}: {nombre}")
                    else:
                        contenedores_existentes += 1
                else:
                    # Tipo desconocido, intentar como contenedor
                    existe = Contenedor.query.filter_by(nombre=nombre).first()
                    
                    if not existe:
                        contenedor_id = f'C{str(siguiente_id_contenedor).zfill(3)}'
                        contenedor = Contenedor(
                            id=contenedor_id,
                            nombre=nombre,
                            tipo=tipo_insumo or 'Contenedor',
                            ubicacion=ubicacion,
                            cantidad_stock=0,
                            cantidad_en_uso=0,
                            cantidad_en_evento=0,
                            costo=0,
                            stock_bajo=5,
                            fecha_actualizacion=date.today()
                        )
                        db.session.add(contenedor)
                        contenedores_creados += 1
                        siguiente_id_contenedor += 1
                        if contenedores_creados <= 10 or contenedores_creados % 20 == 0:
                            print(f"   ✅ Contenedor {contenedores_creados}: {nombre} (tipo: {tipo_insumo})")
            
            except Exception as e:
                print(f"   ❌ Error en: {row.get('nombre', 'desconocido')} - {str(e)}")
                import traceback
                traceback.print_exc()
                errores += 1
    
    # Guardar todos los cambios
    try:
        db.session.commit()
        print(f"\n💾 Cambios guardados en la base de datos")
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error al guardar: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("✅ IMPORTACIÓN COMPLETADA")
    print("=" * 80)
    print(f"\n📊 Resumen:")
    print(f"   • Flores creadas: {flores_creadas}")
    print(f"   • Contenedores creados: {contenedores_creados}")
    print(f"   • Flores existentes (omitidas): {flores_existentes}")
    print(f"   • Contenedores existentes (omitidos): {contenedores_existentes}")
    print(f"   • Errores: {errores}")
    print(f"\n📈 Totales en la base de datos:")
    print(f"   • Total flores: {Flor.query.count()}")
    print(f"   • Total contenedores: {Contenedor.query.count()}")
    print("\n💡 Recarga la página de Insumos en el navegador para verlos")
    print("=" * 80)

