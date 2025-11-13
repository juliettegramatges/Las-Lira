"""
Script para recalcular el total_gastado de todos los clientes
basándose en pedidos activos (no cancelados ni eliminados)
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models.cliente import Cliente
from models.pedido import Pedido
from extensions import db

def recalcular_total_gastado():
    """Recalcula el total_gastado de todos los clientes desde pedidos activos"""
    with app.app_context():
        print("🔄 Recalculando total_gastado de todos los clientes...")
        print("=" * 60)
        
        clientes = Cliente.query.all()
        actualizados = 0
        cambios_significativos = []
        
        for cliente in clientes:
            # Obtener pedidos activos (no cancelados)
            pedidos_activos = Pedido.query.filter(
                Pedido.cliente_id == cliente.id,
                Pedido.estado != 'Cancelado'
            ).all()
            
            # Calcular total real
            total_real = sum((p.precio_ramo or 0) + (p.precio_envio or 0) for p in pedidos_activos)
            total_pedidos_real = len(pedidos_activos)
            
            # Comparar con valores actuales
            total_anterior = float(cliente.total_gastado or 0)
            diferencia = float(total_real) - total_anterior
            
            # Actualizar si hay diferencia
            if abs(diferencia) > 0.01 or cliente.total_pedidos != total_pedidos_real:
                cliente.total_gastado = total_real
                cliente.total_pedidos = total_pedidos_real
                actualizados += 1
                
                if abs(diferencia) > 1000:  # Cambios significativos (>$1,000)
                    cambios_significativos.append({
                        'cliente': cliente.nombre,
                        'id': cliente.id,
                        'anterior': total_anterior,
                        'nuevo': total_real,
                        'diferencia': diferencia,
                        'pedidos_anterior': cliente.total_pedidos,
                        'pedidos_nuevo': total_pedidos_real
                    })
        
        db.session.commit()
        
        print(f"✅ Proceso completado:")
        print(f"   - Clientes procesados: {len(clientes)}")
        print(f"   - Clientes actualizados: {actualizados}")
        
        if cambios_significativos:
            print(f"\n⚠️  Cambios significativos encontrados ({len(cambios_significativos)}):")
            for cambio in cambios_significativos[:10]:  # Mostrar solo los primeros 10
                print(f"   - {cambio['cliente']} (ID: {cambio['id']}):")
                print(f"     Anterior: ${cambio['anterior']:,.0f} ({cambio['pedidos_anterior']} pedidos)")
                print(f"     Nuevo: ${cambio['nuevo']:,.0f} ({cambio['pedidos_nuevo']} pedidos)")
                print(f"     Diferencia: ${cambio['diferencia']:,.0f}")
            if len(cambios_significativos) > 10:
                print(f"   ... y {len(cambios_significativos) - 10} más")
        
        print("\n✅ Recalculación completada exitosamente")

if __name__ == '__main__':
    recalcular_total_gastado()

