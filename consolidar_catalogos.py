#!/usr/bin/env python3
"""
Script para consolidar catálogos de productos
- Mantiene IDs existentes de la base de datos
- Asocia productos de Shopify por nombre
- Agrega productos del catálogo completo
- Preserva compatibilidad con pedidos existentes
"""

import sqlite3
import pandas as pd
import json
from difflib import SequenceMatcher

def similitud_texto(a, b):
    """Calcula la similitud entre dos textos (0-1)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def consolidar_catalogos():
    """
    Consolida los catálogos de productos manteniendo IDs existentes
    """
    print("🔄 Consolidando catálogos de productos...")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('/Users/juliettegramatges/Las-Lira/las_lira.db')
        cursor = conn.cursor()
        
        # 1. Obtener productos existentes de la base de datos
        cursor.execute('''
            SELECT id, nombre, descripcion, precio, categoria, tipo, 
                   imagen_url, sku, peso, tags, metafields, activo
            FROM productos 
            ORDER BY id
        ''')
        
        productos_existentes = cursor.fetchall()
        print(f"📦 Productos existentes en BD: {len(productos_existentes)}")
        
        # 2. Leer catálogo completo
        catalogo_completo = pd.read_csv('catalogo_productos_completo.csv')
        print(f"📋 Productos en catálogo completo: {len(catalogo_completo)}")
        
        # 3. Leer productos de Shopify
        productos_shopify = pd.read_csv('products_export_1.csv')
        print(f"🛍️  Productos en Shopify: {len(productos_shopify)}")
        
        # Crear tabla de mapeo si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mapeo_productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                shopify_handle TEXT,
                shopify_id TEXT,
                metodo_asociacion TEXT,
                similitud REAL,
                fecha_asociacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (producto_id) REFERENCES productos (id)
            )
        ''')
        
        # Limpiar mapeos existentes
        cursor.execute('DELETE FROM mapeo_productos')
        
        # 4. Crear diccionarios para búsqueda rápida
        productos_por_nombre = {}
        for producto in productos_existentes:
            id_prod, nombre, descripcion, precio, categoria, tipo, imagen_url, sku, peso, tags, metafields, activo = producto
            productos_por_nombre[nombre.lower()] = producto
        
        # 5. Procesar productos de Shopify
        productos_shopify_activos = productos_shopify[productos_shopify['Status'] == 'active']
        print(f"🛍️  Productos activos en Shopify: {len(productos_shopify_activos)}")
        
        asociaciones_shopify = 0
        productos_actualizados = 0
        
        for _, row in productos_shopify_activos.iterrows():
            handle = row['Handle']
            titulo = row['Title']
            descripcion = row['Body (HTML)'] if pd.notna(row['Body (HTML)']) else ''
            precio = float(row['Variant Price']) if pd.notna(row['Variant Price']) else 0
            categoria = row['Product Category'] if pd.notna(row['Product Category']) else ''
            tipo = row['Type'] if pd.notna(row['Type']) else ''
            sku = row['Variant SKU'] if pd.notna(row['Variant SKU']) else ''
            peso = float(row['Variant Grams']) if pd.notna(row['Variant Grams']) else 0
            imagen_url = row['Image Src'] if pd.notna(row['Image Src']) else ''
            
            # Buscar coincidencia exacta por nombre
            producto_existente = None
            metodo = ""
            similitud = 0
            
            if titulo.lower() in productos_por_nombre:
                producto_existente = productos_por_nombre[titulo.lower()]
                metodo = "coincidencia_exacta"
                similitud = 1.0
            else:
                # Buscar por similitud
                mejor_match = None
                mejor_similitud = 0
                
                for nombre_existente, producto in productos_por_nombre.items():
                    sim = similitud_texto(titulo, nombre_existente)
                    if sim > mejor_similitud and sim > 0.8:  # Umbral alto para evitar falsos positivos
                        mejor_match = producto
                        mejor_similitud = sim
                
                if mejor_match:
                    producto_existente = mejor_match
                    metodo = "similitud_texto"
                    similitud = mejor_similitud
            
            if producto_existente:
                id_existente, nombre_existente, descripcion_existente, precio_existente, categoria_existente, tipo_existente, imagen_url_existente, sku_existente, peso_existente, tags_existente, metafields_existente, activo_existente = producto_existente
                
                # Registrar mapeo
                cursor.execute('''
                    INSERT INTO mapeo_productos 
                    (producto_id, shopify_handle, shopify_id, metodo_asociacion, similitud)
                    VALUES (?, ?, ?, ?, ?)
                ''', (id_existente, handle, sku, metodo, similitud))
                
                # Actualizar producto existente con datos de Shopify
                cursor.execute('''
                    UPDATE productos SET 
                        descripcion = COALESCE(?, descripcion),
                        categoria = COALESCE(?, categoria),
                        tipo = COALESCE(?, tipo),
                        imagen_url = COALESCE(?, imagen_url),
                        sku = COALESCE(?, sku),
                        peso = COALESCE(?, peso),
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    descripcion if descripcion else None,
                    categoria if categoria else None,
                    tipo if tipo else None,
                    imagen_url if imagen_url else None,
                    sku if sku else None,
                    peso if peso else None,
                    id_existente
                ))
                
                # Copiar imágenes de Shopify
                cursor.execute('''
                    SELECT url, posicion, alt_text
                    FROM imagenes_productos 
                    WHERE producto_id = ?
                    ORDER BY posicion
                ''', (id_existente,))
                
                imagenes_existentes = cursor.fetchall()
                
                # Si no hay imágenes existentes, agregar la de Shopify
                if not imagenes_existentes and imagen_url:
                    cursor.execute('''
                        INSERT INTO imagenes_productos 
                        (producto_id, url, posicion, alt_text, es_principal)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (id_existente, imagen_url, 1, '', 1))
                
                asociaciones_shopify += 1
                productos_actualizados += 1
                
                print(f"✅ {titulo} → {nombre_existente} ({metodo}: {similitud:.2f})")
            else:
                print(f"⚠️  No se encontró asociación para: {titulo}")
        
        # 6. Procesar catálogo completo
        productos_nuevos = 0
        productos_actualizados_catalogo = 0
        
        for _, row in catalogo_completo.iterrows():
            nombre = row['Nombre del producto']
            tipo = row['Tipo de producto'] if pd.notna(row['Tipo de producto']) else ''
            categoria = row['Categoría'] if pd.notna(row['Categoría']) else ''
            precio_str = row['Precio'] if pd.notna(row['Precio']) else '0'
            
            # Limpiar precio
            precio = 0
            if precio_str and precio_str != '':
                try:
                    # Remover $ y puntos, convertir a int
                    precio_limpio = precio_str.replace('$', '').replace('.', '').replace(',', '')
                    precio = int(precio_limpio)
                except:
                    precio = 0
            
            # Buscar si ya existe
            producto_existente = None
            if nombre.lower() in productos_por_nombre:
                producto_existente = productos_por_nombre[nombre.lower()]
            else:
                # Buscar por similitud
                mejor_match = None
                mejor_similitud = 0
                
                for nombre_existente, producto in productos_por_nombre.items():
                    sim = similitud_texto(nombre, nombre_existente)
                    if sim > mejor_similitud and sim > 0.9:  # Umbral muy alto para el catálogo
                        mejor_match = producto
                        mejor_similitud = sim
                
                if mejor_match:
                    producto_existente = mejor_match
            
            if producto_existente:
                # Actualizar producto existente
                id_existente, nombre_existente, descripcion_existente, precio_existente, categoria_existente, tipo_existente, imagen_url_existente, sku_existente, peso_existente, tags_existente, metafields_existente, activo_existente = producto_existente
                
                cursor.execute('''
                    UPDATE productos SET 
                        categoria = COALESCE(?, categoria),
                        tipo = COALESCE(?, tipo),
                        precio = COALESCE(?, precio),
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    categoria if categoria else None,
                    tipo if tipo else None,
                    precio if precio > 0 else None,
                    id_existente
                ))
                
                productos_actualizados_catalogo += 1
                print(f"🔄 Actualizado: {nombre}")
            else:
                # Crear nuevo producto
                cursor.execute('''
                    INSERT INTO productos 
                    (nombre, descripcion, precio, categoria, tipo, imagen_url, sku, peso, tags, metafields, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    nombre,
                    '',  # descripción vacía por ahora
                    precio,
                    categoria,
                    tipo,
                    '',  # imagen vacía por ahora
                    '',  # sku vacío por ahora
                    0,   # peso 0 por ahora
                    '',  # tags vacío por ahora
                    '{}',  # metafields vacío
                    1    # activo
                ))
                
                productos_nuevos += 1
                print(f"➕ Nuevo: {nombre}")
        
        conn.commit()
        
        # 7. Estadísticas finales
        cursor.execute('SELECT COUNT(*) FROM productos WHERE activo = 1')
        total_productos = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM mapeo_productos')
        total_mapeos = cursor.fetchone()[0]
        
        print(f"\n📊 ESTADÍSTICAS FINALES:")
        print(f"   🔗 Asociaciones Shopify: {asociaciones_shopify}")
        print(f"   🔄 Productos actualizados (Shopify): {productos_actualizados}")
        print(f"   🔄 Productos actualizados (Catálogo): {productos_actualizados_catalogo}")
        print(f"   ➕ Productos nuevos: {productos_nuevos}")
        print(f"   📦 Total productos activos: {total_productos}")
        print(f"   🗺️  Total mapeos: {total_mapeos}")
        
        # 8. Mostrar productos sin asociar
        cursor.execute('''
            SELECT p.nombre 
            FROM productos p 
            LEFT JOIN mapeo_productos m ON p.id = m.producto_id 
            WHERE p.activo = 1 AND m.id IS NULL
            ORDER BY p.nombre
        ''')
        
        productos_sin_mapeo = cursor.fetchall()
        if productos_sin_mapeo:
            print(f"\n⚠️  PRODUCTOS SIN MAPEO SHOPIFY ({len(productos_sin_mapeo)}):")
            for producto in productos_sin_mapeo[:10]:  # Mostrar solo los primeros 10
                print(f"   - {producto[0]}")
            if len(productos_sin_mapeo) > 10:
                print(f"   ... y {len(productos_sin_mapeo) - 10} más")
        
        conn.close()
        
        print(f"\n✅ ¡Consolidación completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    consolidar_catalogos()



