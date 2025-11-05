"""
Sincroniza el 'stock en uso' basado en los pedidos 'En Proceso'.

LÓGICA:
-------
1. Resetea cantidad_en_uso = 0 en todas las flores y contenedores
2. Para cada pedido en estado 'En Proceso':
   - Obtiene sus insumos (PedidoInsumo)
   - Incrementa cantidad_en_uso en el inventario correspondiente
3. El stock disponible se calcula automáticamente:
   disponible = stock_total - en_uso - en_evento
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.pedido import Pedido, PedidoInsumo
from models.inventario import Flor, Contenedor
from collections import defaultdict

def sincronizar_stock():
    with app.app_context():
        print('🔄 SINCRONIZANDO STOCK EN USO...')
        print('=' * 60)
        
        # 1. Resetear cantidad_en_uso
        print('\n1️⃣ Reseteando cantidad_en_uso a 0...')
        flores = Flor.query.all()
        contenedores = Contenedor.query.all()
        
        for flor in flores:
            flor.cantidad_en_uso = 0
        
        for contenedor in contenedores:
            contenedor.cantidad_en_uso = 0
        
        print(f'   ✓ {len(flores)} flores reseteadas')
        print(f'   ✓ {len(contenedores)} contenedores reseteados')
        
        # 2. Obtener pedidos "En Proceso"
        print('\n2️⃣ Buscando pedidos "En Proceso"...')
        pedidos_en_proceso = Pedido.query.filter_by(estado='En Proceso').all()
        print(f'   ✓ {len(pedidos_en_proceso)} pedidos encontrados')
        
        if not pedidos_en_proceso:
            db.session.commit()
            print('\n✅ No hay pedidos en proceso. Stock en uso = 0')
            return
        
        # 3. Contabilizar insumos necesarios
        print('\n3️⃣ Contabilizando insumos necesarios...')
        flores_en_uso = defaultdict(int)
        contenedores_en_uso = defaultdict(int)
        
        for pedido in pedidos_en_proceso:
            insumos = PedidoInsumo.query.filter_by(
                pedido_id=pedido.id, 
                descontado_stock=False
            ).all()
            
            print(f'   📦 {pedido.id}: {len(insumos)} insumos')
            
            for insumo in insumos:
                if insumo.insumo_tipo == 'Flor':
                    flores_en_uso[insumo.insumo_id] += insumo.cantidad
                elif insumo.insumo_tipo == 'Contenedor':
                    contenedores_en_uso[insumo.insumo_id] += insumo.cantidad
        
        # 4. Actualizar cantidad_en_uso en inventario
        print('\n4️⃣ Actualizando inventario...')
        
        total_flores_actualizadas = 0
        for flor_id, cantidad in flores_en_uso.items():
            flor = Flor.query.get(flor_id)
            if flor:
                flor.cantidad_en_uso = cantidad
                total_flores_actualizadas += 1
                print(f'   🌸 {flor.tipo} {flor.color}: {cantidad} en uso')
        
        total_contenedores_actualizados = 0
        for contenedor_id, cantidad in contenedores_en_uso.items():
            contenedor = Contenedor.query.get(contenedor_id)
            if contenedor:
                contenedor.cantidad_en_uso = cantidad
                total_contenedores_actualizados += 1
                print(f'   📦 {contenedor.tipo}: {cantidad} en uso')
        
        # 5. Commit
        db.session.commit()
        
        print()
        print('=' * 60)
        print('✅ SINCRONIZACIÓN COMPLETADA')
        print(f'   Pedidos en proceso: {len(pedidos_en_proceso)}')
        print(f'   Flores actualizadas: {total_flores_actualizadas}')
        print(f'   Contenedores actualizados: {total_contenedores_actualizados}')
        print('=' * 60)
        
        # 6. Mostrar resumen de disponibilidad
        print('\n📊 RESUMEN DE STOCK:')
        print('-' * 60)
        
        # Flores con stock en uso
        flores_con_uso = Flor.query.filter(Flor.cantidad_en_uso > 0).all()
        if flores_con_uso:
            print('\n🌸 FLORES EN USO:')
            for f in flores_con_uso:
                print(f'   {f.id}: {f.tipo} {f.color}')
                print(f'      Total: {f.cantidad_stock} | En Uso: {f.cantidad_en_uso} | Disponible: {f.cantidad_disponible}')
        
        # Contenedores con stock en uso
        contenedores_con_uso = Contenedor.query.filter(Contenedor.cantidad_en_uso > 0).all()
        if contenedores_con_uso:
            print('\n📦 CONTENEDORES EN USO:')
            for c in contenedores_con_uso:
                print(f'   {c.id}: {c.tipo}')
                print(f'      Total: {c.stock} | En Uso: {c.cantidad_en_uso} | Disponible: {c.cantidad_disponible}')

if __name__ == '__main__':
    sincronizar_stock()

