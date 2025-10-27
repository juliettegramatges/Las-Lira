"""
Script simple para corregir errores ortográficos en nombres de comunas
Usa SQLite directamente para evitar problemas con Flask context
"""

import sqlite3
import os

# Ruta a la base de datos
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'laslira.db')

# Diccionario de correcciones: {incorrecto: correcto}
CORRECCIONES_COMUNAS = {
    'Huachuraba': 'Huechuraba',
}

def corregir_comunas():
    """Corrige errores ortográficos en comunas"""
    print("\n" + "="*70)
    print("🌸 CORRECCIÓN DE COMUNAS - LAS LIRA")
    print("="*70)
    
    # Conectar a la base de datos
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    total_corregidos = 0
    
    try:
        for comuna_incorrecta, comuna_correcta in CORRECCIONES_COMUNAS.items():
            # Verificar cuántos registros tienen la comuna incorrecta
            cursor.execute(
                "SELECT COUNT(*) FROM pedidos WHERE comuna = ?",
                (comuna_incorrecta,)
            )
            cantidad = cursor.fetchone()[0]
            
            if cantidad > 0:
                print(f"\n📍 '{comuna_incorrecta}' → '{comuna_correcta}'")
                print(f"   Encontrados: {cantidad} pedidos")
                
                # Actualizar los registros
                cursor.execute(
                    "UPDATE pedidos SET comuna = ? WHERE comuna = ?",
                    (comuna_correcta, comuna_incorrecta)
                )
                
                total_corregidos += cantidad
                print(f"   ✅ Corregidos: {cantidad} pedidos")
        
        # Guardar cambios
        if total_corregidos > 0:
            conn.commit()
            print("\n" + "="*70)
            print(f"💾 Cambios guardados: {total_corregidos} pedidos actualizados")
        else:
            print("\n✅ No se encontraron comunas para corregir")
        
        # Mostrar estadísticas actualizadas
        print("\n" + "="*70)
        print("📊 ESTADÍSTICAS DE COMUNAS (TOP 15)")
        print("="*70)
        
        cursor.execute("""
            SELECT comuna, COUNT(*) as cantidad
            FROM pedidos
            WHERE comuna IS NOT NULL AND comuna != ''
            GROUP BY comuna
            ORDER BY cantidad DESC
            LIMIT 15
        """)
        
        print("\n{:<30} {:>10}".format("Comuna", "Pedidos"))
        print("-" * 42)
        
        for row in cursor.fetchall():
            print("{:<30} {:>10}".format(row[0], row[1]))
        
        print("\n" + "="*70)
        print("✨ PROCESO COMPLETADO EXITOSAMENTE")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    corregir_comunas()

