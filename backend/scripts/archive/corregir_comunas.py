"""
Script para corregir errores ortográficos en nombres de comunas
"""

import sys
import os

# Agregar el directorio backend al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from extensions import db
from models.pedido import Pedido
from models.cliente import Cliente
import app

# Diccionario de correcciones: {incorrecto: correcto}
CORRECCIONES_COMUNAS = {
    'Huachuraba': 'Huechuraba',
    # Agregar más correcciones aquí si se encuentran
}

def corregir_comunas_pedidos():
    """Corrige errores ortográficos en comunas de pedidos"""
    print("\n" + "="*70)
    print("🔧 CORRECCIÓN DE COMUNAS EN PEDIDOS")
    print("="*70)
    
    total_corregidos = 0
    
    for comuna_incorrecta, comuna_correcta in CORRECCIONES_COMUNAS.items():
        # Buscar pedidos con la comuna incorrecta
        pedidos = Pedido.query.filter(Pedido.comuna == comuna_incorrecta).all()
        cantidad = len(pedidos)
        
        if cantidad > 0:
            print(f"\n📍 '{comuna_incorrecta}' → '{comuna_correcta}'")
            print(f"   Encontrados: {cantidad} pedidos")
            
            # Actualizar cada pedido
            for pedido in pedidos:
                pedido.comuna = comuna_correcta
            
            total_corregidos += cantidad
            print(f"   ✅ Corregidos: {cantidad} pedidos")
    
    return total_corregidos

def corregir_comunas_clientes():
    """Corrige errores ortográficos en direcciones de clientes"""
    print("\n" + "="*70)
    print("🔧 CORRECCIÓN DE COMUNAS EN CLIENTES")
    print("="*70)
    
    total_corregidos = 0
    
    for comuna_incorrecta, comuna_correcta in CORRECCIONES_COMUNAS.items():
        # Buscar clientes cuya dirección principal contenga la comuna incorrecta
        clientes = Cliente.query.filter(
            Cliente.direccion_principal.like(f'%{comuna_incorrecta}%')
        ).all()
        
        if clientes:
            print(f"\n📍 '{comuna_incorrecta}' → '{comuna_correcta}' en direcciones")
            print(f"   Encontrados: {len(clientes)} clientes")
            
            for cliente in clientes:
                if cliente.direccion_principal:
                    cliente.direccion_principal = cliente.direccion_principal.replace(
                        comuna_incorrecta, comuna_correcta
                    )
                    total_corregidos += 1
            
            print(f"   ✅ Corregidos: {len(clientes)} clientes")
    
    return total_corregidos

def mostrar_estadisticas():
    """Muestra estadísticas de comunas después de la corrección"""
    print("\n" + "="*70)
    print("📊 ESTADÍSTICAS DE COMUNAS (TOP 15)")
    print("="*70)
    
    # Consultar las top 15 comunas
    resultado = db.session.execute(db.text("""
        SELECT comuna, COUNT(*) as cantidad
        FROM pedidos
        WHERE comuna IS NOT NULL AND comuna != ''
        GROUP BY comuna
        ORDER BY cantidad DESC
        LIMIT 15
    """))
    
    print("\n{:<30} {:>10}".format("Comuna", "Pedidos"))
    print("-" * 42)
    
    for row in resultado:
        print("{:<30} {:>10}".format(row[0], row[1]))

if __name__ == '__main__':
    print("\n🌸 CORRECCIÓN DE COMUNAS - LAS LIRA")
    print("="*70)
    
    try:
        # Corregir pedidos
        pedidos_corregidos = corregir_comunas_pedidos()
        
        # Corregir clientes
        clientes_corregidos = corregir_comunas_clientes()
        
        # Guardar cambios
        if pedidos_corregidos > 0 or clientes_corregidos > 0:
            print("\n" + "="*70)
            print("💾 GUARDANDO CAMBIOS...")
            db.session.commit()
            print("✅ Cambios guardados exitosamente")
            
            print("\n📈 RESUMEN:")
            print(f"   • Pedidos corregidos: {pedidos_corregidos}")
            print(f"   • Clientes corregidos: {clientes_corregidos}")
            print(f"   • Total: {pedidos_corregidos + clientes_corregidos}")
        else:
            print("\n✅ No se encontraron comunas para corregir")
        
        # Mostrar estadísticas actualizadas
        mostrar_estadisticas()
        
        print("\n" + "="*70)
        print("✨ PROCESO COMPLETADO EXITOSAMENTE")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.session.rollback()
        import traceback
        traceback.print_exc()
        sys.exit(1)

