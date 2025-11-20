#!/usr/bin/env python3
"""
Script para extraer y organizar productos de Shopify con sus imágenes
Convierte el CSV de export de Shopify en una base de datos más útil
"""

import pandas as pd
import requests
import os
import json
from urllib.parse import urlparse
import sqlite3
from datetime import datetime

def extraer_productos_shopify(csv_path='products_export_1.csv'):
    """
    Extrae productos del CSV de Shopify y los organiza con sus imágenes
    """
    print("🛍️  Extrayendo productos de Shopify...")
    
    # Leer el CSV
    df = pd.read_csv(csv_path)
    
    # Filtrar solo productos activos y con título
    productos_activos = df[
        (df['Status'] == 'active') & 
        (df['Title'].notna()) & 
        (df['Title'] != '')
    ].copy()
    
    print(f"📊 Total de productos activos encontrados: {len(productos_activos)}")
    
    # Agrupar por Handle (producto único)
    productos_unicos = []
    
    for handle in productos_activos['Handle'].unique():
        if pd.isna(handle):
            continue
            
        # Obtener todas las filas para este producto
        producto_rows = productos_activos[productos_activos['Handle'] == handle]
        
        # Tomar la primera fila como base del producto
        producto_base = producto_rows.iloc[0]
        
        # Extraer todas las imágenes
        imagenes = []
        for _, row in producto_rows.iterrows():
            if pd.notna(row['Image Src']) and row['Image Src'] != '':
                imagenes.append({
                    'url': row['Image Src'],
                    'position': int(row['Image Position']) if pd.notna(row['Image Position']) else 999,
                    'alt_text': row['Image Alt Text'] if pd.notna(row['Image Alt Text']) else ''
                })
        
        # Ordenar imágenes por posición
        imagenes.sort(key=lambda x: x['position'])
        
        # Crear objeto del producto
        producto = {
            'handle': handle,
            'titulo': producto_base['Title'],
            'descripcion': producto_base['Body (HTML)'] if pd.notna(producto_base['Body (HTML)']) else '',
            'categoria': producto_base['Product Category'] if pd.notna(producto_base['Product Category']) else '',
            'tipo': producto_base['Type'] if pd.notna(producto_base['Type']) else '',
            'tags': producto_base['Tags'] if pd.notna(producto_base['Tags']) else '',
            'precio': float(producto_base['Variant Price']) if pd.notna(producto_base['Variant Price']) else 0,
            'precio_comparacion': float(producto_base['Variant Compare At Price']) if pd.notna(producto_base['Variant Compare At Price']) else None,
            'sku': producto_base['Variant SKU'] if pd.notna(producto_base['Variant SKU']) else '',
            'peso': float(producto_base['Variant Grams']) if pd.notna(producto_base['Variant Grams']) else 0,
            'imagenes': imagenes,
            'imagen_principal': imagenes[0]['url'] if imagenes else None,
            'total_imagenes': len(imagenes),
            'metafields': {
                'color': producto_base['Color (product.metafields.shopify.color-pattern)'] if pd.notna(producto_base['Color (product.metafields.shopify.color-pattern)']) else '',
                'material': producto_base['Material de decoración (product.metafields.shopify.decoration-material)'] if pd.notna(producto_base['Material de decoración (product.metafields.shopify.decoration-material)']) else '',
                'formato_papel': producto_base['Formato de papel (product.metafields.shopify.paper-format)'] if pd.notna(producto_base['Formato de papel (product.metafields.shopify.paper-format)']) else '',
                'tamaño_papel': producto_base['Tamaño de papel (product.metafields.shopify.paper-size)'] if pd.notna(producto_base['Tamaño de papel (product.metafields.shopify.paper-size)']) else '',
                'caracteristicas_planta': producto_base['Características de la planta (product.metafields.shopify.plant-characteristics)'] if pd.notna(producto_base['Características de la planta (product.metafields.shopify.plant-characteristics)']) else '',
                'forma': producto_base['Forma (product.metafields.shopify.shape)'] if pd.notna(producto_base['Forma (product.metafields.shopify.shape)']) else '',
                'espacio_adecuado': producto_base['Espacio adecuado (product.metafields.shopify.suitable-space)'] if pd.notna(producto_base['Espacio adecuado (product.metafields.shopify.suitable-space)']) else '',
                'luz_solar': producto_base['Luz solar (product.metafields.shopify.sunlight)'] if pd.notna(producto_base['Luz solar (product.metafields.shopify.sunlight)']) else '',
                'forma_jarrón': producto_base['Forma de jarrón (product.metafields.shopify.vase-shape)'] if pd.notna(producto_base['Forma de jarrón (product.metafields.shopify.vase-shape)']) else ''
            }
        }
        
        productos_unicos.append(producto)
    
    print(f"✅ Productos únicos procesados: {len(productos_unicos)}")
    return productos_unicos

def guardar_en_base_datos(productos, db_path='productos_shopify.db'):
    """
    Guarda los productos en una base de datos SQLite
    """
    print("💾 Guardando en base de datos...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Crear tabla de productos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos_shopify (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            handle TEXT UNIQUE NOT NULL,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            categoria TEXT,
            tipo TEXT,
            tags TEXT,
            precio REAL,
            precio_comparacion REAL,
            sku TEXT,
            peso REAL,
            imagen_principal TEXT,
            total_imagenes INTEGER,
            metafields TEXT,
            fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Crear tabla de imágenes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS imagenes_productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_handle TEXT,
            url TEXT NOT NULL,
            posicion INTEGER,
            alt_text TEXT,
            FOREIGN KEY (producto_handle) REFERENCES productos_shopify (handle)
        )
    ''')
    
    # Limpiar datos existentes
    cursor.execute('DELETE FROM imagenes_productos')
    cursor.execute('DELETE FROM productos_shopify')
    
    # Insertar productos
    for producto in productos:
        cursor.execute('''
            INSERT INTO productos_shopify 
            (handle, titulo, descripcion, categoria, tipo, tags, precio, precio_comparacion, 
             sku, peso, imagen_principal, total_imagenes, metafields)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            producto['handle'],
            producto['titulo'],
            producto['descripcion'],
            producto['categoria'],
            producto['tipo'],
            producto['tags'],
            producto['precio'],
            producto['precio_comparacion'],
            producto['sku'],
            producto['peso'],
            producto['imagen_principal'],
            producto['total_imagenes'],
            json.dumps(producto['metafields'])
        ))
        
        # Insertar imágenes
        for img in producto['imagenes']:
            cursor.execute('''
                INSERT INTO imagenes_productos (producto_handle, url, posicion, alt_text)
                VALUES (?, ?, ?, ?)
            ''', (
                producto['handle'],
                img['url'],
                img['position'],
                img['alt_text']
            ))
    
    conn.commit()
    conn.close()
    
    print(f"✅ Base de datos guardada en: {db_path}")

def generar_reporte(productos):
    """
    Genera un reporte de los productos extraídos
    """
    print("\n📊 REPORTE DE PRODUCTOS EXTRAÍDOS")
    print("=" * 50)
    
    # Estadísticas generales
    total_productos = len(productos)
    productos_con_imagenes = len([p for p in productos if p['total_imagenes'] > 0])
    total_imagenes = sum(p['total_imagenes'] for p in productos)
    
    print(f"📦 Total productos: {total_productos}")
    print(f"🖼️  Productos con imágenes: {productos_con_imagenes}")
    print(f"📸 Total de imágenes: {total_imagenes}")
    
    # Por categoría
    categorias = {}
    for producto in productos:
        cat = producto['categoria'] or 'Sin categoría'
        categorias[cat] = categorias.get(cat, 0) + 1
    
    print(f"\n📂 Productos por categoría:")
    for cat, count in sorted(categorias.items(), key=lambda x: x[1], reverse=True):
        print(f"   {cat}: {count}")
    
    # Por tipo
    tipos = {}
    for producto in productos:
        tipo = producto['tipo'] or 'Sin tipo'
        tipos[tipo] = tipos.get(tipo, 0) + 1
    
    print(f"\n🏷️  Productos por tipo:")
    for tipo, count in sorted(tipos.items(), key=lambda x: x[1], reverse=True):
        print(f"   {tipo}: {count}")
    
    # Rango de precios
    precios = [p['precio'] for p in productos if p['precio'] > 0]
    if precios:
        print(f"\n💰 Rango de precios:")
        print(f"   Mínimo: ${min(precios):,.0f}")
        print(f"   Máximo: ${max(precios):,.0f}")
        print(f"   Promedio: ${sum(precios)/len(precios):,.0f}")

def main():
    """
    Función principal
    """
    print("🌸 EXTRACTOR DE PRODUCTOS SHOPIFY - LAS LIRA")
    print("=" * 50)
    
    # Verificar que existe el archivo CSV
    csv_path = 'products_export_1.csv'
    if not os.path.exists(csv_path):
        print(f"❌ No se encontró el archivo: {csv_path}")
        return
    
    try:
        # Extraer productos
        productos = extraer_productos_shopify(csv_path)
        
        # Guardar en base de datos
        guardar_en_base_datos(productos)
        
        # Generar reporte
        generar_reporte(productos)
        
        print(f"\n✅ ¡Proceso completado exitosamente!")
        print(f"📁 Archivo de base de datos: productos_shopify.db")
        
    except Exception as e:
        print(f"❌ Error durante el proceso: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()



