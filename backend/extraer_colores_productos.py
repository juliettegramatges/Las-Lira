#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extraer todos los colores únicos de los productos
"""

import sqlite3
import re

DB_PATH = 'instance/laslira.db'

def normalizar_color(color):
    """Normaliza un color eliminando espacios y capitalizando correctamente"""
    color = color.strip()
    # Capitalizar primera letra
    return color.capitalize()

def extraer_colores():
    """Extrae todos los colores únicos de los productos"""
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Obtener todos los colores_asociados
    cursor.execute("SELECT colores_asociados FROM productos WHERE colores_asociados IS NOT NULL AND colores_asociados != ''")
    resultados = cursor.fetchall()
    
    colores_set = set()
    
    for (colores_texto,) in resultados:
        # Dividir por comas
        colores_lista = colores_texto.split(',')
        
        for color in colores_lista:
            color_limpio = color.strip()
            
            # Remover paréntesis y su contenido
            color_limpio = re.sub(r'\([^)]*\)', '', color_limpio).strip()
            
            # Si contiene "y", dividir
            if ' y ' in color_limpio:
                partes = color_limpio.split(' y ')
                for parte in partes:
                    if parte.strip():
                        colores_set.add(normalizar_color(parte.strip()))
            else:
                if color_limpio:
                    colores_set.add(normalizar_color(color_limpio))
    
    conn.close()
    
    # Ordenar alfabéticamente
    colores_ordenados = sorted(list(colores_set))
    
    print("=" * 80)
    print("🎨 COLORES ÚNICOS ENCONTRADOS")
    print("=" * 80)
    print(f"\nTotal de colores únicos: {len(colores_ordenados)}\n")
    
    for i, color in enumerate(colores_ordenados, 1):
        print(f"{i:3}. {color}")
    
    print("\n" + "=" * 80)
    print("✅ EXTRACCIÓN COMPLETADA")
    print("=" * 80)
    
    # Generar lista para Python
    print("\n# Lista de colores para usar en el código:")
    print("COLORES_PREDEFINIDOS = [")
    for color in colores_ordenados:
        print(f"    '{color}',")
    print("]")
    
    return colores_ordenados

if __name__ == '__main__':
    extraer_colores()


