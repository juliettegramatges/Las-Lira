#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para importar productos desde el catálogo CSV
"""

import sys
from pathlib import Path
import csv

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db
from models.producto import Producto

print("=" * 80)
print("🎨 IMPORTANDO PRODUCTOS DESDE CATÁLOGO CSV")
print("=" * 80)

# Buscar el archivo más reciente del catálogo
csv_dir = backend_dir.parent
catalogo_files = list(csv_dir.glob('catalogo_productos_completo*.csv'))

if not catalogo_files:
    print(f"❌ No se encontró el catálogo en: {csv_dir}")
    sys.exit(1)

# Ordenar por fecha de modificación y tomar el más reciente
csv_path = max(catalogo_files, key=lambda p: p.stat().st_mtime)

print(f"\n📄 Leyendo: {csv_path.name}")

with app.app_context():
    productos_creados = 0
    productos_actualizados = 0
    errores = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Mapear nombres de columnas del CSV
        # Nombre,Tipo de producto,Categoría,Es planta,Contenedor,Material,Colores,Flores y/o Follajes,Variantes_Tamaños,Dimensiones_Tamaños,Variantes_Ruedo,Variantes_Colores,Precio S,Precio M,Cuidados
        
        for idx, row in enumerate(reader, start=1):
            try:
                nombre = row.get('Nombre', '').strip()
                
                if not nombre:
                    continue
                
                tipo_producto = row.get('Tipo de producto', '').strip()
                categoria = row.get('Categoría', '').strip()
                es_planta = row.get('Es planta', 'No').strip().lower() == 'sí'
                contenedor = row.get('Contenedor', '').strip()
                material = row.get('Material', '').strip()
                colores = row.get('Colores', '').strip()
                flores_follajes = row.get('Flores y/o Follajes', '').strip()
                
                variantes_tamanos = row.get('Variantes_Tamaños', '').strip()
                dimensiones_tamanos = row.get('Dimensiones_Tamaños', '').strip()
                variantes_ruedo = row.get('Variantes_Ruedo', '').strip()
                variantes_colores = row.get('Variantes_Colores', '').strip()
                
                # Precios (puede haber Precio S, Precio M, Precio L, o solo Precio)
                precio_s = row.get('Precio S', row.get('Precio', '')).strip()
                precio_m = row.get('Precio M', '').strip()
                precio_l = row.get('Precio L', '').strip()
                
                # Limpiar precios (quitar $, puntos, comas)
                def limpiar_precio(p):
                    if not p or p.lower() == 'variable':
                        return 0
                    p = p.replace('$', '').replace('.', '').replace(',', '').strip()
                    try:
                        return int(p)
                    except:
                        return 0
                
                precio_venta = limpiar_precio(precio_s if precio_s else precio_m)
                
                cuidados = row.get('Cuidados', '').strip()
                
                # Determinar tipo de arreglo basado en contenedor
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
                
                # Crear descripción combinada
                descripcion_parts = []
                if tipo_producto:
                    descripcion_parts.append(tipo_producto)
                if flores_follajes:
                    descripcion_parts.append(f"Flores: {flores_follajes}")
                if contenedor and contenedor.lower() != 'sin florero (ramo)':
                    descripcion_parts.append(f"Contenedor: {contenedor}")
                
                descripcion = '. '.join(descripcion_parts) if descripcion_parts else nombre
                
                # Buscar producto existente por nombre
                producto_existente = Producto.query.filter_by(nombre=nombre).first()
                
                if producto_existente:
                    # Actualizar
                    producto_existente.descripcion = descripcion
                    producto_existente.tipo_arreglo = tipo_arreglo
                    producto_existente.colores_asociados = colores or variantes_colores
                    producto_existente.flores_asociadas = flores_follajes
                    producto_existente.tipos_macetero = contenedor
                    producto_existente.precio_venta = precio_venta
                    producto_existente.cuidados = cuidados
                    producto_existente.disponible_shopify = True
                    
                    productos_actualizados += 1
                    if productos_actualizados <= 5:
                        print(f"   🔄 Actualizado: {nombre}")
                else:
                    # Crear nuevo
                    producto_id = f'PR{idx:04d}'
                    
                    producto = Producto(
                        id=producto_id,
                        nombre=nombre,
                        descripcion=descripcion,
                        tipo_arreglo=tipo_arreglo,
                        colores_asociados=colores or variantes_colores,
                        flores_asociadas=flores_follajes,
                        tipos_macetero=contenedor,
                        vista_360_180=variantes_ruedo or None,
                        tamano=variantes_tamanos or dimensiones_tamanos or None,
                        precio_venta=precio_venta,
                        cuidados=cuidados,
                        disponible_shopify=True
                    )
                    
                    db.session.add(producto)
                    productos_creados += 1
                    if productos_creados <= 5:
                        print(f"   ✨ Creado: {nombre}")
            
            except Exception as e:
                print(f"   ❌ Error en fila {idx} ({nombre}): {e}")
                errores += 1
    
    try:
        db.session.commit()
        print("\n   ✅ Cambios guardados en la base de datos")
    except Exception as e:
        print(f"\n   ❌ Error al guardar: {e}")
        db.session.rollback()
    
    print("\n" + "=" * 80)
    print("✅ IMPORTACIÓN COMPLETADA")
    print("=" * 80)
    print(f"\n📊 Resumen:")
    print(f"   • Productos creados: {productos_creados}")
    print(f"   • Productos actualizados: {productos_actualizados}")
    print(f"   • Errores: {errores}")
    
    # Verificar total en DB
    total_productos = db.session.query(Producto).count()
    print(f"\n   • Total productos en DB: {total_productos}")
    
    print("\n💡 Recarga el navegador y ve a 'Productos'")
    print("=" * 80)


