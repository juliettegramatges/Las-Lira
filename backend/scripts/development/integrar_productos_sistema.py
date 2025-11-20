#!/usr/bin/env python3
"""
Script para integrar los productos de Shopify con el sistema actual de Las Lira
Actualiza la tabla de productos existente con datos de Shopify
"""

import sqlite3
import json
from datetime import datetime

def integrar_con_sistema_actual(db_shopify='productos_shopify.db', db_sistema='las_lira.db'):
    """
    Integra los productos de Shopify con el sistema actual
    """
    print("🔄 Integrando productos de Shopify con el sistema actual...")
    
    # Conectar a ambas bases de datos
    conn_shopify = sqlite3.connect(db_shopify)
    conn_sistema = sqlite3.connect(db_sistema)
    
    cursor_shopify = conn_shopify.cursor()
    cursor_sistema = conn_sistema.cursor()
    
    # Obtener productos de Shopify
    cursor_shopify.execute('''
        SELECT handle, titulo, descripcion, categoria, tipo, tags, precio, 
               precio_comparacion, sku, peso, imagen_principal, total_imagenes, metafields
        FROM productos_shopify
    ''')
    
    productos_shopify = cursor_shopify.fetchall()
    
    print(f"📦 Productos encontrados en Shopify: {len(productos_shopify)}")
    
    # Verificar si existe la tabla productos en el sistema
    cursor_sistema.execute('''
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='productos'
    ''')
    
    if not cursor_sistema.fetchone():
        print("📋 Creando tabla productos...")
        cursor_sistema.execute('''
            CREATE TABLE productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                precio REAL,
                categoria TEXT,
                tipo TEXT,
                imagen_url TEXT,
                sku TEXT,
                peso REAL,
                tags TEXT,
                metafields TEXT,
                activo BOOLEAN DEFAULT 1,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    # Limpiar productos existentes (opcional - comentar si quieres mantener los existentes)
    # cursor_sistema.execute('DELETE FROM productos')
    
    productos_actualizados = 0
    productos_nuevos = 0
    
    for producto in productos_shopify:
        handle, titulo, descripcion, categoria, tipo, tags, precio, precio_comparacion, sku, peso, imagen_principal, total_imagenes, metafields_json = producto
        
        # Verificar si el producto ya existe
        cursor_sistema.execute('SELECT id FROM productos WHERE sku = ? OR nombre = ?', (sku, titulo))
        producto_existente = cursor_sistema.fetchone()
        
        metafields = json.loads(metafields_json) if metafields_json else {}
        
        if producto_existente:
            # Actualizar producto existente
            cursor_sistema.execute('''
                UPDATE productos SET 
                    nombre = ?, descripcion = ?, precio = ?, categoria = ?, 
                    tipo = ?, imagen_url = ?, peso = ?, tags = ?, metafields = ?,
                    fecha_actualizacion = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (titulo, descripcion, precio, categoria, tipo, imagen_principal, peso, tags, metafields_json, producto_existente[0]))
            productos_actualizados += 1
        else:
            # Insertar nuevo producto
            cursor_sistema.execute('''
                INSERT INTO productos 
                (nombre, descripcion, precio, categoria, tipo, imagen_url, sku, peso, tags, metafields)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (titulo, descripcion, precio, categoria, tipo, imagen_principal, sku, peso, tags, metafields_json))
            productos_nuevos += 1
    
    conn_sistema.commit()
    
    # Crear tabla de imágenes si no existe
    cursor_sistema.execute('''
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='imagenes_productos'
    ''')
    
    if not cursor_sistema.fetchone():
        print("📸 Creando tabla de imágenes...")
        cursor_sistema.execute('''
            CREATE TABLE imagenes_productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                producto_id INTEGER,
                url TEXT NOT NULL,
                posicion INTEGER,
                alt_text TEXT,
                es_principal BOOLEAN DEFAULT 0,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (producto_id) REFERENCES productos (id)
            )
        ''')
    
    # Integrar imágenes
    print("🖼️  Integrando imágenes...")
    cursor_shopify.execute('''
        SELECT p.titulo, i.url, i.posicion, i.alt_text
        FROM imagenes_productos i
        JOIN productos_shopify p ON i.producto_handle = p.handle
        ORDER BY p.titulo, i.posicion
    ''')
    
    imagenes = cursor_shopify.fetchall()
    
    for titulo, url, posicion, alt_text in imagenes:
        # Obtener el ID del producto en el sistema
        cursor_sistema.execute('SELECT id FROM productos WHERE nombre = ?', (titulo,))
        producto_id = cursor_sistema.fetchone()
        
        # Si no se encuentra por nombre exacto, buscar por nombre similar
        if not producto_id:
            cursor_sistema.execute('SELECT id FROM productos WHERE nombre LIKE ?', (f'%{titulo}%',))
            producto_id = cursor_sistema.fetchone()
        
        if producto_id:
            # Verificar si la imagen ya existe
            cursor_sistema.execute('''
                SELECT id FROM imagenes_productos 
                WHERE producto_id = ? AND url = ?
            ''', (producto_id[0], url))
            
            if not cursor_sistema.fetchone():
                cursor_sistema.execute('''
                    INSERT INTO imagenes_productos 
                    (producto_id, url, posicion, alt_text, es_principal)
                    VALUES (?, ?, ?, ?, ?)
                ''', (producto_id[0], url, posicion, alt_text, 1 if posicion == 1 else 0))
    
    conn_sistema.commit()
    
    # Estadísticas finales
    cursor_sistema.execute('SELECT COUNT(*) FROM productos')
    total_productos = cursor_sistema.fetchone()[0]
    
    cursor_sistema.execute('SELECT COUNT(*) FROM imagenes_productos')
    total_imagenes = cursor_sistema.fetchone()[0]
    
    print(f"\n✅ Integración completada:")
    print(f"   📦 Productos nuevos: {productos_nuevos}")
    print(f"   🔄 Productos actualizados: {productos_actualizados}")
    print(f"   📊 Total productos en sistema: {total_productos}")
    print(f"   🖼️  Total imágenes: {total_imagenes}")
    
    conn_shopify.close()
    conn_sistema.close()

def crear_endpoint_api():
    """
    Crea un endpoint en el backend para servir los productos con imágenes
    """
    print("🔌 Endpoint API creado en: backend/routes/productos_routes.py")
    print("📋 Recuerda registrar el blueprint en app.py:")
    print("   from routes.productos_routes import bp as productos_bp")
    print("   app.register_blueprint(productos_bp, url_prefix='/api/productos')")

def main():
    """
    Función principal
    """
    print("🌸 INTEGRADOR DE PRODUCTOS SHOPIFY - LAS LIRA")
    print("=" * 50)
    
    try:
        # Integrar con sistema actual
        integrar_con_sistema_actual()
        
        # Crear endpoint API
        crear_endpoint_api()
        
        print(f"\n✅ ¡Integración completada exitosamente!")
        print(f"🔗 Para usar los productos en tu frontend, agrega el endpoint a tu backend")
        
    except Exception as e:
        print(f"❌ Error durante la integración: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
