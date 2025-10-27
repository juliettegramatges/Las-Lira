#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para mejorar el sistema de personalizaciones
Agrega campos para análisis y trazabilidad de pedidos personalizados
"""

import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app import app
from extensions import db

print("=" * 80)
print("🎨 MEJORANDO SISTEMA DE PERSONALIZACIONES")
print("=" * 80)

with app.app_context():
    try:
        inspector = db.inspect(db.engine)
        
        # ========================================
        # 1. AGREGAR CAMPOS A TABLA PRODUCTOS
        # ========================================
        print("\n📦 Mejorando tabla PRODUCTOS...")
        
        productos_columns = [col['name'] for col in inspector.get_columns('productos')]
        
        # Campo: es_personalizacion (BOOLEAN)
        if 'es_personalizacion' not in productos_columns:
            with db.engine.connect() as connection:
                connection.execute(db.text(
                    'ALTER TABLE productos ADD COLUMN es_personalizacion BOOLEAN DEFAULT FALSE'
                ))
                connection.commit()
            print("   ✅ Agregado: es_personalizacion")
        else:
            print("   ℹ️  Campo 'es_personalizacion' ya existe")
        
        # Campo: categoria_personalizacion (VARCHAR)
        if 'categoria_personalizacion' not in productos_columns:
            with db.engine.connect() as connection:
                connection.execute(db.text(
                    'ALTER TABLE productos ADD COLUMN categoria_personalizacion VARCHAR(100)'
                ))
                connection.commit()
            print("   ✅ Agregado: categoria_personalizacion")
        else:
            print("   ℹ️  Campo 'categoria_personalizacion' ya existe")
        
        # ========================================
        # 2. AGREGAR CAMPOS A TABLA PEDIDOS
        # ========================================
        print("\n📝 Mejorando tabla PEDIDOS...")
        
        pedidos_columns = [col['name'] for col in inspector.get_columns('pedidos')]
        
        # Campo: colores_solicitados (TEXT) - JSON con colores del pedido
        if 'colores_solicitados' not in pedidos_columns:
            with db.engine.connect() as connection:
                connection.execute(db.text(
                    'ALTER TABLE pedidos ADD COLUMN colores_solicitados TEXT'
                ))
                connection.commit()
            print("   ✅ Agregado: colores_solicitados")
        else:
            print("   ℹ️  Campo 'colores_solicitados' ya existe")
        
        # Campo: tipo_personalizacion (VARCHAR)
        if 'tipo_personalizacion' not in pedidos_columns:
            with db.engine.connect() as connection:
                connection.execute(db.text(
                    'ALTER TABLE pedidos ADD COLUMN tipo_personalizacion VARCHAR(100)'
                ))
                connection.commit()
            print("   ✅ Agregado: tipo_personalizacion")
        else:
            print("   ℹ️  Campo 'tipo_personalizacion' ya existe")
        
        # Campo: notas_personalizacion (TEXT)
        if 'notas_personalizacion' not in pedidos_columns:
            with db.engine.connect() as connection:
                connection.execute(db.text(
                    'ALTER TABLE pedidos ADD COLUMN notas_personalizacion TEXT'
                ))
                connection.commit()
            print("   ✅ Agregado: notas_personalizacion")
        else:
            print("   ℹ️  Campo 'notas_personalizacion' ya existe")
        
        # ========================================
        # 3. MARCAR PRODUCTO "PERSONALIZACIÓN"
        # ========================================
        print("\n🎨 Configurando producto 'Personalización'...")
        
        from models.producto import Producto
        
        personalizacion = Producto.query.filter_by(nombre='Personalización').first()
        
        if personalizacion:
            personalizacion.es_personalizacion = True
            personalizacion.categoria_personalizacion = 'General'
            personalizacion.tipo_arreglo = 'Personalizado'
            db.session.commit()
            print(f"   ✅ Producto 'Personalización' marcado (ID: {personalizacion.id})")
        else:
            print("   ⚠️  Producto 'Personalización' no encontrado. Créalo primero con:")
            print("      python3 backend/scripts/agregar_personalizacion.py")
        
        # ========================================
        # 4. RESUMEN
        # ========================================
        print("\n" + "=" * 80)
        print("✅ MIGRACIÓN COMPLETADA")
        print("=" * 80)
        
        print("\n📊 NUEVOS CAMPOS AGREGADOS:\n")
        
        print("🎨 TABLA: productos")
        print("   • es_personalizacion (BOOLEAN)")
        print("     → TRUE si es un producto personalizable")
        print("   • categoria_personalizacion (VARCHAR)")
        print("     → Subcategoría: 'Ramo', 'Centro de Mesa', 'Bouquet', etc.")
        
        print("\n📝 TABLA: pedidos")
        print("   • colores_solicitados (TEXT)")
        print("     → JSON: ['Rojo', 'Blanco', 'Verde']")
        print("   • tipo_personalizacion (VARCHAR)")
        print("     → 'Ramo', 'Centro de Mesa', 'Arreglo Especial', etc.")
        print("   • notas_personalizacion (TEXT)")
        print("     → Notas específicas de la personalización")
        
        print("\n" + "=" * 80)
        print("📈 AHORA PUEDES ANALIZAR PERSONALIZACIONES CON:")
        print("=" * 80)
        print("""
1. Filtrar productos personalizables:
   SELECT * FROM productos WHERE es_personalizacion = TRUE

2. Filtrar pedidos personalizados:
   SELECT * FROM pedidos 
   WHERE producto_id IN (
       SELECT id FROM productos WHERE es_personalizacion = TRUE
   )

3. Análisis de insumos en personalizaciones:
   SELECT pi.*, p.cliente_nombre, p.motivo
   FROM pedidos_insumos pi
   JOIN pedidos p ON p.id = pi.pedido_id
   JOIN productos prod ON prod.id = p.producto_id
   WHERE prod.es_personalizacion = TRUE

4. Colores más usados en personalizaciones:
   SELECT colores_solicitados, COUNT(*) as cantidad
   FROM pedidos
   WHERE producto_id IN (
       SELECT id FROM productos WHERE es_personalizacion = TRUE
   )
   GROUP BY colores_solicitados
   ORDER BY cantidad DESC

5. Tipos de personalización más populares:
   SELECT tipo_personalizacion, COUNT(*) as cantidad
   FROM pedidos
   WHERE tipo_personalizacion IS NOT NULL
   GROUP BY tipo_personalizacion
   ORDER BY cantidad DESC
        """)
        
        print("=" * 80)
        print("🎯 SIGUIENTE PASO:")
        print("   Actualiza los modelos Python para incluir estos campos")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()

print("\n✅ Script finalizado\n")

