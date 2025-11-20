#!/usr/bin/env python3
"""
Script para asociar productos existentes con los nuevos de Shopify
Mantiene la compatibilidad con pedidos existentes
"""

import sqlite3
import json
from difflib import SequenceMatcher

def similitud_texto(a, b):
    """Calcula la similitud entre dos textos (0-1)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def asociar_productos():
    """
    Asocia productos existentes con los nuevos de Shopify
    """
    print("🔄 Asociando productos existentes con Shopify...")
    
    try:
        # Conectar a la base de datos
        conn = sqlite3.connect('las_lira.db')
        cursor = conn.cursor()
        
        # Obtener productos existentes (sin los de Shopify)
        cursor.execute('''
            SELECT id, nombre, descripcion, precio, categoria, tipo, 
                   imagen_url, sku, peso, tags, metafields, activo
            FROM productos 
            WHERE activo = 1 AND sku IS NULL OR sku = ''
            ORDER BY nombre
        ''')
        
        productos_existentes = cursor.fetchall()
        print(f"📦 Productos existentes encontrados: {len(productos_existentes)}")
        
        # Obtener productos de Shopify
        cursor.execute('''
            SELECT id, nombre, descripcion, precio, categoria, tipo, 
                   imagen_url, sku, peso, tags, metafields, activo
            FROM productos 
            WHERE activo = 1 AND sku IS NOT NULL AND sku != ''
            ORDER BY nombre
        ''')
        
        productos_shopify = cursor.fetchall()
        print(f"🛍️  Productos de Shopify encontrados: {len(productos_shopify)}")
        
        # Crear tabla de asociaciones si no existe
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS asociaciones_productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_existente_id INTEGER,
                producto_shopify_id INTEGER,
                similitud REAL,
                metodo_asociacion TEXT,
                fecha_asociacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (producto_existente_id) REFERENCES productos (id),
                FOREIGN KEY (producto_shopify_id) REFERENCES productos (id)
            )
        ''')
        
        # Limpiar asociaciones existentes
        cursor.execute('DELETE FROM asociaciones_productos')
        
        asociaciones_realizadas = 0
        productos_actualizados = 0
        
        for producto_existente in productos_existentes:
            id_existente, nombre_existente, descripcion_existente, precio_existente, categoria_existente, tipo_existente, imagen_url_existente, sku_existente, peso_existente, tags_existente, metafields_existente, activo_existente = producto_existente
            
            mejor_match = None
            mejor_similitud = 0
            metodo = ""
            
            # Buscar coincidencia exacta por nombre
            for producto_shopify in productos_shopify:
                id_shopify, nombre_shopify, descripcion_shopify, precio_shopify, categoria_shopify, tipo_shopify, imagen_url_shopify, sku_shopify, peso_shopify, tags_shopify, metafields_shopify, activo_shopify = producto_shopify
                
                if nombre_existente.lower() == nombre_shopify.lower():
                    mejor_match = producto_shopify
                    mejor_similitud = 1.0
                    metodo = "coincidencia_exacta"
                    break
            
            # Si no hay coincidencia exacta, buscar por similitud
            if not mejor_match:
                for producto_shopify in productos_shopify:
                    id_shopify, nombre_shopify, descripcion_shopify, precio_shopify, categoria_shopify, tipo_shopify, imagen_url_shopify, sku_shopify, peso_shopify, tags_shopify, metafields_shopify, activo_shopify = producto_shopify
                    
                    similitud = similitud_texto(nombre_existente, nombre_shopify)
                    
                    if similitud > mejor_similitud and similitud > 0.7:  # Umbral de similitud
                        mejor_match = producto_shopify
                        mejor_similitud = similitud
                        metodo = "similitud_texto"
            
            # Si encontramos una asociación
            if mejor_match:
                id_shopify, nombre_shopify, descripcion_shopify, precio_shopify, categoria_shopify, tipo_shopify, imagen_url_shopify, sku_shopify, peso_shopify, tags_shopify, metafields_shopify, activo_shopify = mejor_match
                
                # Registrar la asociación
                cursor.execute('''
                    INSERT INTO asociaciones_productos 
                    (producto_existente_id, producto_shopify_id, similitud, metodo_asociacion)
                    VALUES (?, ?, ?, ?)
                ''', (id_existente, id_shopify, mejor_similitud, metodo))
                
                # Actualizar el producto existente con datos de Shopify
                cursor.execute('''
                    UPDATE productos SET 
                        descripcion = COALESCE(?, descripcion),
                        categoria = COALESCE(?, categoria),
                        tipo = COALESCE(?, tipo),
                        imagen_url = COALESCE(?, imagen_url),
                        sku = ?,
                        peso = COALESCE(?, peso),
                        tags = COALESCE(?, tags),
                        metafields = COALESCE(?, metafields),
                        fecha_actualizacion = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (
                    descripcion_shopify if descripcion_shopify else None,
                    categoria_shopify if categoria_shopify else None,
                    tipo_shopify if tipo_shopify else None,
                    imagen_url_shopify if imagen_url_shopify else None,
                    sku_shopify,
                    peso_shopify if peso_shopify else None,
                    tags_shopify if tags_shopify else None,
                    metafields_shopify if metafields_shopify else None,
                    id_existente
                ))
                
                # Copiar imágenes del producto de Shopify al existente
                cursor.execute('''
                    SELECT url, posicion, alt_text, es_principal
                    FROM imagenes_productos 
                    WHERE producto_id = ?
                    ORDER BY posicion
                ''', (id_shopify,))
                
                imagenes_shopify = cursor.fetchall()
                
                # Eliminar imágenes existentes del producto
                cursor.execute('DELETE FROM imagenes_productos WHERE producto_id = ?', (id_existente,))
                
                # Copiar imágenes de Shopify
                for img_url, pos, alt, es_principal in imagenes_shopify:
                    cursor.execute('''
                        INSERT INTO imagenes_productos 
                        (producto_id, url, posicion, alt_text, es_principal)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (id_existente, img_url, pos, alt, es_principal))
                
                asociaciones_realizadas += 1
                productos_actualizados += 1
                
                print(f"✅ {nombre_existente} → {nombre_shopify} ({metodo}: {mejor_similitud:.2f})")
            else:
                print(f"⚠️  No se encontró asociación para: {nombre_existente}")
        
        conn.commit()
        
        # Estadísticas finales
        cursor.execute('SELECT COUNT(*) FROM productos WHERE activo = 1')
        total_productos = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM imagenes_productos')
        total_imagenes = cursor.fetchone()[0]
        
        print(f"\n📊 ESTADÍSTICAS FINALES:")
        print(f"   🔗 Asociaciones realizadas: {asociaciones_realizadas}")
        print(f"   🔄 Productos actualizados: {productos_actualizados}")
        print(f"   📦 Total productos activos: {total_productos}")
        print(f"   🖼️  Total imágenes: {total_imagenes}")
        
        # Mostrar productos sin asociar
        cursor.execute('''
            SELECT p.nombre 
            FROM productos p 
            LEFT JOIN asociaciones_productos a ON p.id = a.producto_existente_id 
            WHERE p.activo = 1 AND a.id IS NULL AND (p.sku IS NULL OR p.sku = '')
        ''')
        
        productos_sin_asociar = cursor.fetchall()
        if productos_sin_asociar:
            print(f"\n⚠️  PRODUCTOS SIN ASOCIAR ({len(productos_sin_asociar)}):")
            for producto in productos_sin_asociar:
                print(f"   - {producto[0]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asociar_productos()



