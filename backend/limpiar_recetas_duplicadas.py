"""
Limpia recetas duplicadas en productos.
Similar al script de pedidos, pero para RecetaProducto.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.producto import Producto, RecetaProducto
from collections import defaultdict

def limpiar_recetas():
    with app.app_context():
        productos = Producto.query.all()
        
        total_eliminados = 0
        productos_afectados = 0
        
        print('🔍 Buscando recetas duplicadas...\n')
        
        for producto in productos:
            recetas = RecetaProducto.query.filter_by(producto_id=producto.id).all()
            
            if not recetas:
                continue
            
            # Agrupar por tipo + id
            grupos = defaultdict(list)
            for receta in recetas:
                key = f'{receta.insumo_tipo}-{receta.insumo_id}'
                grupos[key].append(receta)
            
            # Ver si hay duplicados
            eliminados_producto = 0
            for key, lista_recetas in grupos.items():
                if len(lista_recetas) > 1:
                    # Mantener el primero
                    mantener = lista_recetas[0]
                    # Eliminar los demás
                    for receta_dup in lista_recetas[1:]:
                        db.session.delete(receta_dup)
                        eliminados_producto += 1
                        total_eliminados += 1
            
            if eliminados_producto > 0:
                productos_afectados += 1
                print(f'✅ {producto.id} ({producto.nombre}): Eliminados {eliminados_producto} insumos duplicados')
                print(f'   Antes: {len(recetas)} insumos → Después: {len(recetas) - eliminados_producto} insumos')
        
        # Confirmar cambios
        db.session.commit()
        
        print()
        print('=' * 60)
        print(f'✅ LIMPIEZA COMPLETADA')
        print(f'   Productos afectados: {productos_afectados}')
        print(f'   Recetas duplicadas eliminadas: {total_eliminados}')
        print('=' * 60)

if __name__ == '__main__':
    limpiar_recetas()

