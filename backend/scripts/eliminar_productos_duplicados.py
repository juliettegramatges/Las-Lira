"""
Script para eliminar productos duplicados
Mantiene solo el ID original con el precio correcto
"""

import sys
import os
import sqlite3

# Añadir el directorio backend al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from extensions import db
from app import app
from sqlalchemy import text

def encontrar_id_original(duplicados):
    """
    Encuentra el ID original entre los duplicados
    Prioridad: PR00XX > número simple > PROD_XXX
    Los duplicados son tuplas: (id, nombre, precio_venta, precio)
    """
    # Ordenar por tipo de ID
    pr_ids = [d for d in duplicados if str(d[0]).startswith('PR')]
    num_ids = [d for d in duplicados if str(d[0]).isdigit()]
    prod_ids = [d for d in duplicados if str(d[0]).startswith('PROD_')]

    # Prioridad: PR > número > PROD
    if pr_ids:
        # Entre los PR, tomar el que tiene precio
        con_precio = [p for p in pr_ids if (p[2] or 0) > 0 or (p[3] or 0) > 0]
        return con_precio[0] if con_precio else pr_ids[0]
    elif num_ids:
        con_precio = [p for p in num_ids if (p[2] or 0) > 0 or (p[3] or 0) > 0]
        return con_precio[0] if con_precio else num_ids[0]
    else:
        return prod_ids[0] if prod_ids else duplicados[0]

def obtener_mejor_precio(duplicados):
    """Obtiene el mejor precio entre los duplicados"""
    precios = []
    for d in duplicados:
        precio = d[2] or d[3] or 0  # precio_venta o precio
        if precio > 0:
            precios.append(precio)
    return max(precios) if precios else 0

def limpiar_duplicados():
    """Limpia productos duplicados usando SQL directo"""

    with app.app_context():
        print("="*80)
        print("🧹 LIMPIEZA DE PRODUCTOS DUPLICADOS")
        print("="*80)

        # Conectar a la base de datos
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance', 'laslira.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Contar productos iniciales
        cursor.execute("SELECT COUNT(*) FROM productos")
        total_inicial = cursor.fetchone()[0]
        print(f"\n📊 Total productos antes de limpieza: {total_inicial}")

        # Obtener todos los productos con su información
        cursor.execute("SELECT id, nombre, precio_venta, precio FROM productos ORDER BY nombre")
        productos = cursor.fetchall()

        # Agrupar por nombre (case-insensitive)
        grupos = {}
        for p in productos:
            nombre_key = p[1].lower().strip() if p[1] else ''
            if nombre_key not in grupos:
                grupos[nombre_key] = []
            grupos[nombre_key].append(p)

        # Encontrar duplicados
        duplicados = {k: v for k, v in grupos.items() if len(v) > 1}
        print(f"📦 Productos únicos: {len(grupos) - len(duplicados)}")
        print(f"⚠️  Grupos con duplicados: {len(duplicados)}")

        productos_eliminados = 0
        recetas_migradas = 0
        pedidos_actualizados = 0

        for nombre_key, grupo in duplicados.items():
            if not nombre_key:
                continue

            print(f"\n🔍 Procesando: {grupo[0][1]}")
            print(f"   Duplicados encontrados: {len(grupo)}")

            # Encontrar el ID original
            original = encontrar_id_original(grupo)
            mejor_precio = obtener_mejor_precio(grupo)

            original_id = original[0]
            precio_actual = original[2] or original[3] or 0

            # Actualizar precio del original si es necesario
            if mejor_precio > 0 and precio_actual == 0:
                cursor.execute(
                    "UPDATE productos SET precio_venta = ?, precio = ? WHERE id = ?",
                    (mejor_precio, mejor_precio, original_id)
                )
                print(f"   💰 Actualizando precio a ${mejor_precio:,.0f}")

            print(f"   ✅ ID original: {original_id} (precio: ${max(mejor_precio, precio_actual):,.0f})")

            # Procesar cada duplicado
            for dup in grupo:
                dup_id = dup[0]
                if dup_id == original_id:
                    continue

                print(f"   🗑️  Eliminando duplicado: {dup_id}")

                # 1. Verificar y migrar recetas
                cursor.execute("SELECT COUNT(*) FROM recetas_productos WHERE producto_id = ?", (dup_id,))
                num_recetas_dup = cursor.fetchone()[0]

                if num_recetas_dup > 0:
                    cursor.execute("SELECT COUNT(*) FROM recetas_productos WHERE producto_id = ?", (original_id,))
                    num_recetas_original = cursor.fetchone()[0]

                    if num_recetas_original == 0:
                        # Migrar las recetas
                        cursor.execute(
                            "UPDATE recetas_productos SET producto_id = ? WHERE producto_id = ?",
                            (original_id, dup_id)
                        )
                        recetas_migradas += num_recetas_dup
                        print(f"      📋 Migradas {num_recetas_dup} recetas")
                    else:
                        # El original ya tiene recetas, eliminar las del duplicado
                        cursor.execute("DELETE FROM recetas_productos WHERE producto_id = ?", (dup_id,))
                        print(f"      📋 Eliminadas {num_recetas_dup} recetas (original ya tiene recetas)")

                # 2. Actualizar pedidos que usan este producto
                cursor.execute("SELECT COUNT(*) FROM pedidos_productos WHERE producto_id = ?", (dup_id,))
                num_pedidos = cursor.fetchone()[0]
                if num_pedidos > 0:
                    cursor.execute(
                        "UPDATE pedidos_productos SET producto_id = ? WHERE producto_id = ?",
                        (original_id, dup_id)
                    )
                    pedidos_actualizados += num_pedidos

                # 3. Eliminar el producto duplicado
                cursor.execute("DELETE FROM productos WHERE id = ?", (dup_id,))
                productos_eliminados += 1

        # Commit todos los cambios
        conn.commit()

        # Contar productos finales
        cursor.execute("SELECT COUNT(*) FROM productos")
        total_final = cursor.fetchone()[0]

        conn.close()

        print("\n" + "="*80)
        print("✅ LIMPIEZA COMPLETADA")
        print("="*80)
        print(f"   Productos eliminados: {productos_eliminados}")
        print(f"   Recetas migradas: {recetas_migradas}")
        print(f"   Referencias en pedidos actualizadas: {pedidos_actualizados}")
        print(f"   Total productos después: {total_final}")
        print("="*80)

if __name__ == '__main__':
    limpiar_duplicados()
