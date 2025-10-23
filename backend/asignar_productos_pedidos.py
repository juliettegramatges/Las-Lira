#!/usr/bin/env python3
"""
Asigna productos a pedidos que no los tienen
"""

import sys
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.pedido import Pedido
from models.producto import Producto, RecetaProducto
from models.inventario import Flor, Contenedor

def asignar_productos():
    """Asigna productos a pedidos sin producto_id"""
    with app.app_context():
        print("🔧 Asignando productos a pedidos...")
        
        # Obtener todos los productos disponibles
        productos = Producto.query.all()
        if not productos:
            print("❌ No hay productos en la BD")
            return
        
        print(f"📦 Productos disponibles: {len(productos)}")
        for p in productos:
            print(f"   • {p.id}: {p.nombre}")
        
        # Obtener pedidos sin producto
        pedidos_sin_producto = Pedido.query.filter(
            (Pedido.producto_id == None) | (Pedido.producto_id == '')
        ).all()
        
        print(f"\n📝 Pedidos sin producto: {len(pedidos_sin_producto)}")
        
        # Mapeo de nombres comunes a productos
        mapeo = {
            'Amor Eterno': 'PR001',
            'Pasión Roja': 'PR001',
            'Rosas Rojas': 'PR001',
            'Ramo Rosas': 'PR001',
            'Elegancia Blanca': 'PR002',
            'Rosas Blancas': 'PR002',
            'Lirios': 'PR002',
            'Dulce Encanto': 'PR003',
            'Rosadas': 'PR003',
            'Campo Silvestre': 'PR004',
            'Mix': 'PR004',
            'Sol Radiante': 'PR005',
            'Girasoles': 'PR005',
            'Dulce Lirio': 'PR006',
            'Orquídea': 'PR008',
            'Ramo Clásico': 'PR009',
        }
        
        count = 0
        for pedido in pedidos_sin_producto:
            # Intentar asignar por nombre
            producto_id = None
            arreglo = pedido.arreglo_pedido or ''
            
            # Buscar en el mapeo
            for key, value in mapeo.items():
                if key.lower() in arreglo.lower():
                    producto_id = value
                    break
            
            # Si no encuentra, asignar el primer producto por defecto
            if not producto_id:
                producto_id = productos[count % len(productos)].id
            
            pedido.producto_id = producto_id
            count += 1
            print(f"  ✓ {pedido.id}: {arreglo[:30]}... → {producto_id}")
        
        db.session.commit()
        print(f"\n✅ {count} pedidos actualizados")
        
        # Ahora copiar insumos
        print("\n🔧 Copiando insumos de productos a pedidos...")
        
        todos_pedidos = Pedido.query.all()
        count_insumos = 0
        count_pedidos = 0
        
        for pedido in todos_pedidos:
            if not pedido.producto_id:
                continue
            
            # Verificar si ya tiene insumos
            from models.pedido import PedidoInsumo
            insumos_existentes = PedidoInsumo.query.filter_by(pedido_id=pedido.id).count()
            if insumos_existentes > 0:
                print(f"  ⏭️  {pedido.id} ya tiene {insumos_existentes} insumos")
                continue
            
            # Buscar receta del producto
            recetas = RecetaProducto.query.filter_by(producto_id=pedido.producto_id).all()
            
            if not recetas:
                print(f"  ⚠️  Producto {pedido.producto_id} no tiene receta")
                continue
            
            # Copiar cada insumo de la receta al pedido
            for receta in recetas:
                # Obtener costo unitario
                costo_unitario = 0
                tipo_insumo_lower = receta.insumo_tipo.lower() if receta.insumo_tipo else ''
                
                if tipo_insumo_lower == 'flor':
                    insumo = Flor.query.get(receta.insumo_id)
                    costo_unitario = insumo.costo_unitario if insumo else 0
                elif tipo_insumo_lower == 'contenedor':
                    insumo = Contenedor.query.get(receta.insumo_id)
                    costo_unitario = insumo.costo if insumo else 0
                
                costo_total = costo_unitario * receta.cantidad
                
                nuevo_insumo = PedidoInsumo(
                    pedido_id=pedido.id,
                    insumo_tipo=receta.insumo_tipo,  # Usar el valor original
                    insumo_id=receta.insumo_id,
                    cantidad=receta.cantidad,
                    costo_unitario=costo_unitario,
                    costo_total=costo_total,
                    descontado_stock=False
                )
                db.session.add(nuevo_insumo)
                count_insumos += 1
            
            count_pedidos += 1
            print(f"  ✓ {pedido.id}: {len(recetas)} insumos copiados")
        
        db.session.commit()
        print(f"\n✅ {count_insumos} insumos copiados a {count_pedidos} pedidos")
        
        print("\n" + "="*60)
        print("✨ COMPLETADO")
        print("="*60)

if __name__ == "__main__":
    asignar_productos()

