"""
Script para eliminar insumos duplicados de pedidos.
Mantiene solo UNA copia de cada insumo único.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.pedido import PedidoInsumo
from collections import defaultdict

def limpiar_duplicados():
    with app.app_context():
        # Obtener todos los pedidos únicos
        pedidos = db.session.query(PedidoInsumo.pedido_id).distinct().all()
        
        total_eliminados = 0
        pedidos_afectados = 0
        
        for (pedido_id,) in pedidos:
            # Obtener todos los insumos del pedido
            insumos = PedidoInsumo.query.filter_by(pedido_id=pedido_id).all()
            
            # Agrupar por tipo + id
            grupos = defaultdict(list)
            for insumo in insumos:
                key = f'{insumo.insumo_tipo}-{insumo.insumo_id}'
                grupos[key].append(insumo)
            
            # Para cada grupo, mantener solo el primero y eliminar el resto
            eliminados_pedido = 0
            for key, lista_insumos in grupos.items():
                if len(lista_insumos) > 1:
                    # Mantener el primero
                    mantener = lista_insumos[0]
                    # Eliminar los demás
                    for insumo_dup in lista_insumos[1:]:
                        db.session.delete(insumo_dup)
                        eliminados_pedido += 1
                        total_eliminados += 1
            
            if eliminados_pedido > 0:
                pedidos_afectados += 1
                print(f'✅ {pedido_id}: Eliminados {eliminados_pedido} insumos duplicados')
        
        # Confirmar cambios
        db.session.commit()
        
        print()
        print('=' * 60)
        print(f'✅ LIMPIEZA COMPLETADA')
        print(f'   Pedidos afectados: {pedidos_afectados}')
        print(f'   Insumos duplicados eliminados: {total_eliminados}')
        print('=' * 60)

if __name__ == '__main__':
    limpiar_duplicados()

