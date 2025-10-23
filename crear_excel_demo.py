#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para crear archivos Excel demo para el sistema de gestión de florería Las-Lira
"""

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from datetime import datetime, timedelta
import random

def crear_estilo_header(ws, row=1):
    """Aplica estilo a la fila de encabezado"""
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF", size=11)
    
    for cell in ws[row]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center")

def crear_inventario_flores():
    """Crea archivo de inventario de flores"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Flores"
    
    # Encabezados
    headers = ["ID", "Tipo de Flor", "Color", "Proveedor", "Costo Unitario", "Cantidad Stock", "Bodega", "Unidad", "Última Actualización"]
    ws.append(headers)
    crear_estilo_header(ws)
    
    # Datos demo
    flores = [
        ["FL001", "Rosa", "Rojo", "Flores del Valle", 1500, 120, "Bodega 1", "Tallo", "2025-10-20"],
        ["FL002", "Rosa", "Blanco", "Flores del Valle", 1500, 85, "Bodega 1", "Tallo", "2025-10-20"],
        ["FL003", "Rosa", "Rosado", "Flores del Valle", 1500, 95, "Bodega 1", "Tallo", "2025-10-20"],
        ["FL004", "Rosa", "Amarillo", "Flores del Valle", 1500, 60, "Bodega 2", "Tallo", "2025-10-21"],
        ["FL005", "Lirio", "Blanco", "Jardín Central", 2500, 45, "Bodega 1", "Tallo", "2025-10-19"],
        ["FL006", "Lirio", "Rosado", "Jardín Central", 2500, 38, "Bodega 1", "Tallo", "2025-10-19"],
        ["FL007", "Girasol", "Amarillo", "Campo Florido", 2000, 30, "Bodega 2", "Tallo", "2025-10-22"],
        ["FL008", "Clavel", "Rojo", "Flores del Valle", 800, 150, "Bodega 1", "Tallo", "2025-10-20"],
        ["FL009", "Clavel", "Blanco", "Flores del Valle", 800, 140, "Bodega 1", "Tallo", "2025-10-20"],
        ["FL010", "Clavel", "Rosado", "Flores del Valle", 800, 130, "Bodega 2", "Tallo", "2025-10-20"],
        ["FL011", "Tulipán", "Rojo", "Jardín Central", 2200, 25, "Bodega 1", "Tallo", "2025-10-18"],
        ["FL012", "Tulipán", "Amarillo", "Jardín Central", 2200, 20, "Bodega 1", "Tallo", "2025-10-18"],
        ["FL013", "Hortensia", "Azul", "Campo Florido", 3500, 15, "Bodega 2", "Ramo", "2025-10-21"],
        ["FL014", "Hortensia", "Rosado", "Campo Florido", 3500, 18, "Bodega 2", "Ramo", "2025-10-21"],
        ["FL015", "Gerbera", "Naranja", "Flores del Valle", 1800, 55, "Bodega 1", "Tallo", "2025-10-20"],
        ["FL016", "Gerbera", "Rosado", "Flores del Valle", 1800, 48, "Bodega 1", "Tallo", "2025-10-20"],
        ["FL017", "Orquídea", "Blanco", "Jardín Central", 5000, 12, "Bodega 2", "Tallo", "2025-10-19"],
        ["FL018", "Alstroemeria", "Morado", "Campo Florido", 1200, 70, "Bodega 1", "Tallo", "2025-10-22"],
        ["FL019", "Eucalipto", "Verde", "Campo Florido", 500, 200, "Bodega 1", "Rama", "2025-10-21"],
        ["FL020", "Solidago", "Amarillo", "Flores del Valle", 600, 100, "Bodega 2", "Rama", "2025-10-20"],
    ]
    
    for fila in flores:
        ws.append(fila)
    
    # Ajustar anchos de columna
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 15
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 18
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 15
    ws.column_dimensions['G'].width = 12
    ws.column_dimensions['H'].width = 10
    ws.column_dimensions['I'].width = 18
    
    wb.save("01_Inventario_Flores.xlsx")
    print("✅ Archivo '01_Inventario_Flores.xlsx' creado")

def crear_inventario_contenedores():
    """Crea archivo de inventario de contenedores (floreros, maceteros, canastos)"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Contenedores"
    
    # Encabezados
    headers = ["ID", "Tipo", "Material", "Forma", "Tamaño", "Color", "Costo", "Stock", "Bodega", "Última Actualización"]
    ws.append(headers)
    crear_estilo_header(ws)
    
    # Datos demo
    contenedores = [
        ["CO001", "Florero", "Vidrio", "Cilíndrico", "Grande (30cm)", "Transparente", 3500, 15, "Bodega 1", "2025-10-15"],
        ["CO002", "Florero", "Vidrio", "Cilíndrico", "Mediano (20cm)", "Transparente", 2500, 22, "Bodega 1", "2025-10-15"],
        ["CO003", "Florero", "Vidrio", "Cilíndrico", "Pequeño (15cm)", "Transparente", 1500, 30, "Bodega 2", "2025-10-15"],
        ["CO004", "Florero", "Cerámica", "Redondo", "Mediano (18cm)", "Blanco", 4000, 12, "Bodega 1", "2025-10-18"],
        ["CO005", "Florero", "Cerámica", "Cuadrado", "Pequeño (12cm)", "Negro", 3000, 18, "Bodega 1", "2025-10-18"],
        ["CO006", "Macetero", "Cerámica", "Redondo", "Grande (25cm)", "Terracota", 5000, 10, "Bodega 2", "2025-10-19"],
        ["CO007", "Macetero", "Cerámica", "Redondo", "Mediano (18cm)", "Terracota", 3500, 15, "Bodega 2", "2025-10-19"],
        ["CO008", "Macetero", "Cerámica", "Redondo", "Pequeño (12cm)", "Terracota", 2000, 25, "Bodega 2", "2025-10-19"],
        ["CO009", "Macetero", "Plástico", "Redondo", "Mediano (18cm)", "Blanco", 1500, 30, "Bodega 1", "2025-10-20"],
        ["CO010", "Canasto", "Mimbre", "Rectangular", "Grande (35cm)", "Natural", 4500, 8, "Bodega 1", "2025-10-16"],
        ["CO011", "Canasto", "Mimbre", "Rectangular", "Mediano (25cm)", "Natural", 3000, 12, "Bodega 1", "2025-10-16"],
        ["CO012", "Canasto", "Mimbre", "Redondo", "Pequeño (20cm)", "Natural", 2500, 15, "Bodega 2", "2025-10-16"],
        ["CO013", "Florero", "Vidrio", "Burbuja", "Pequeño (10cm)", "Transparente", 2000, 20, "Bodega 1", "2025-10-17"],
        ["CO014", "Macetero", "Cerámica", "Cuadrado", "Grande (30cm)", "Gris", 6000, 6, "Bodega 2", "2025-10-21"],
        ["CO015", "Canasto", "Mimbre", "Ovalado", "Mediano (28cm)", "Natural", 3500, 10, "Bodega 1", "2025-10-16"],
    ]
    
    for fila in contenedores:
        ws.append(fila)
    
    # Ajustar anchos
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 12
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 14
    ws.column_dimensions['E'].width = 18
    ws.column_dimensions['F'].width = 14
    ws.column_dimensions['G'].width = 10
    ws.column_dimensions['H'].width = 8
    ws.column_dimensions['I'].width = 12
    ws.column_dimensions['J'].width = 18
    
    wb.save("02_Inventario_Contenedores.xlsx")
    print("✅ Archivo '02_Inventario_Contenedores.xlsx' creado")

def crear_productos_catalogo():
    """Crea archivo con catálogo de productos (arreglos predefinidos)"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Catálogo Productos"
    
    # Encabezados
    headers = ["ID", "Nombre Producto", "Descripción", "Tipo", "Paleta de Colores", "Cantidad Flores", "Precio Venta", "Foto", "Disponible en Shopify"]
    ws.append(headers)
    crear_estilo_header(ws)
    
    # Productos demo
    productos = [
        ["PR001", "Pasión Roja", "Arreglo elegante en tonos rojos", "Con Florero", "Rojo, Verde", "12-15", 35000, "passion-roja.jpg", "Sí"],
        ["PR002", "Sueño Blanco", "Delicado arreglo en blancos puros", "Con Florero", "Blanco, Verde", "10-12", 32000, "sueno-blanco.jpg", "Sí"],
        ["PR003", "Jardín Primaveral", "Mezcla de colores vibrantes", "Con Florero", "Multicolor", "15-18", 42000, "jardin-primaveral.jpg", "Sí"],
        ["PR004", "Elegancia Rosa", "Rosas rosadas en florero", "Con Florero", "Rosado, Verde", "12-15", 38000, "elegancia-rosa.jpg", "Sí"],
        ["PR005", "Sol Radiante", "Girasoles y flores amarillas", "Con Florero", "Amarillo, Naranja", "8-10", 30000, "sol-radiante.jpg", "Sí"],
        ["PR006", "Dulce Lirio", "Lirios blancos y rosados", "Con Florero", "Blanco, Rosado", "6-8", 45000, "dulce-lirio.jpg", "Sí"],
        ["PR007", "Campo Silvestre", "Arreglo rústico en canasto", "Con Canasto", "Multicolor", "20-25", 48000, "campo-silvestre.jpg", "Sí"],
        ["PR008", "Orquídea Imperial", "Orquídeas blancas premium", "Con Macetero", "Blanco", "3-5", 55000, "orquidea-imperial.jpg", "Sí"],
        ["PR009", "Ramo Clásico", "Ramo de rosas rojas", "Sin Contenedor", "Rojo", "12", 28000, "ramo-clasico.jpg", "Sí"],
        ["PR010", "Amor Eterno", "Caja con rosas y chocolates", "Con Caja", "Rojo, Rosado", "24", 65000, "amor-eterno.jpg", "Sí"],
        ["PR011", "Naturaleza Viva", "Mix de flores de temporada", "Con Canasto", "Multicolor", "18-20", 40000, "naturaleza-viva.jpg", "Sí"],
        ["PR012", "Serenidad Azul", "Hortensias azules", "Con Macetero", "Azul, Verde", "5-7", 50000, "serenidad-azul.jpg", "Sí"],
    ]
    
    for fila in productos:
        ws.append(fila)
    
    # Ajustar anchos
    ws.column_dimensions['A'].width = 8
    ws.column_dimensions['B'].width = 18
    ws.column_dimensions['C'].width = 30
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 20
    ws.column_dimensions['F'].width = 15
    ws.column_dimensions['G'].width = 12
    ws.column_dimensions['H'].width = 20
    ws.column_dimensions['I'].width = 18
    
    wb.save("03_Catalogo_Productos.xlsx")
    print("✅ Archivo '03_Catalogo_Productos.xlsx' creado")

def crear_pedidos():
    """Crea archivo de pedidos con estados"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Pedidos"
    
    # Encabezados
    headers = ["ID Pedido", "Fecha", "Canal", "Cliente", "Teléfono", "Producto/Descripción", "Estado", "Precio", "Dirección Entrega", "Fecha Entrega", "Notas"]
    ws.append(headers)
    crear_estilo_header(ws)
    
    # Datos demo de pedidos
    estados = ["Recibido", "En Preparación", "Listo", "Despachado", "Entregado"]
    canales = ["Shopify", "WhatsApp"]
    
    pedidos = [
        ["PED001", "2025-10-20", "Shopify", "María González", "+56912345601", "PR001 - Pasión Roja", "Entregado", 35000, "Las Condes, Santiago", "2025-10-21", "Entregado 10:30 AM"],
        ["PED002", "2025-10-21", "WhatsApp", "Carlos Pérez", "+56912345602", "Arreglo personalizado tonos rosados", "Entregado", 40000, "Providencia, Santiago", "2025-10-22", "Cliente pidió más lirios"],
        ["PED003", "2025-10-22", "Shopify", "Ana Martínez", "+56912345603", "PR003 - Jardín Primaveral", "Despachado", 42000, "Vitacura, Santiago", "2025-10-23", "En camino"],
        ["PED004", "2025-10-22", "Shopify", "Roberto Silva", "+56912345604", "PR006 - Dulce Lirio", "Listo", 45000, "Ñuñoa, Santiago", "2025-10-23", "Listo para despacho"],
        ["PED005", "2025-10-23", "WhatsApp", "Patricia Rojas", "+56912345605", "Canasto con girasoles y rosas amarillas", "En Preparación", 48000, "La Reina, Santiago", "2025-10-24", "Urgente: cumpleaños"],
        ["PED006", "2025-10-23", "Shopify", "Luis Vargas", "+56912345606", "PR010 - Amor Eterno", "En Preparación", 65000, "San Miguel, Santiago", "2025-10-25", "Incluir tarjeta"],
        ["PED007", "2025-10-23", "Shopify", "Carmen López", "+56912345607", "PR004 - Elegancia Rosa", "Recibido", 38000, "Maipú, Santiago", "2025-10-24", ""],
        ["PED008", "2025-10-23", "WhatsApp", "Diego Fernández", "+56912345608", "Ramo de 24 rosas rojas sin contenedor", "Recibido", 55000, "Las Condes, Santiago", "2025-10-24", "Para propuesta matrimonio"],
    ]
    
    for fila in pedidos:
        ws.append(fila)
    
    # Ajustar anchos
    ws.column_dimensions['A'].width = 10
    ws.column_dimensions['B'].width = 12
    ws.column_dimensions['C'].width = 10
    ws.column_dimensions['D'].width = 18
    ws.column_dimensions['E'].width = 15
    ws.column_dimensions['F'].width = 35
    ws.column_dimensions['G'].width = 15
    ws.column_dimensions['H'].width = 10
    ws.column_dimensions['I'].width = 25
    ws.column_dimensions['J'].width = 14
    ws.column_dimensions['K'].width = 30
    
    wb.save("04_Pedidos.xlsx")
    print("✅ Archivo '04_Pedidos.xlsx' creado")

def crear_recetas_productos():
    """Crea archivo con las 'recetas' de cada producto (qué insumos necesita)"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Recetas"
    
    # Encabezados
    headers = ["ID Producto", "Nombre Producto", "ID Insumo", "Tipo Insumo", "Descripción Insumo", "Cantidad Necesaria", "Unidad"]
    ws.append(headers)
    crear_estilo_header(ws)
    
    # Recetas demo
    recetas = [
        # Pasión Roja (PR001)
        ["PR001", "Pasión Roja", "FL001", "Flor", "Rosa Roja", "12", "Tallos"],
        ["PR001", "Pasión Roja", "FL019", "Flor", "Eucalipto Verde", "5", "Ramas"],
        ["PR001", "Pasión Roja", "CO002", "Contenedor", "Florero Vidrio Mediano", "1", "Unidad"],
        
        # Sueño Blanco (PR002)
        ["PR002", "Sueño Blanco", "FL002", "Flor", "Rosa Blanco", "10", "Tallos"],
        ["PR002", "Sueño Blanco", "FL005", "Flor", "Lirio Blanco", "2", "Tallos"],
        ["PR002", "Sueño Blanco", "FL019", "Flor", "Eucalipto Verde", "3", "Ramas"],
        ["PR002", "Sueño Blanco", "CO002", "Contenedor", "Florero Vidrio Mediano", "1", "Unidad"],
        
        # Jardín Primaveral (PR003)
        ["PR003", "Jardín Primaveral", "FL015", "Flor", "Gerbera Naranja", "5", "Tallos"],
        ["PR003", "Jardín Primaveral", "FL016", "Flor", "Gerbera Rosado", "5", "Tallos"],
        ["PR003", "Jardín Primaveral", "FL018", "Flor", "Alstroemeria Morado", "5", "Tallos"],
        ["PR003", "Jardín Primaveral", "FL020", "Flor", "Solidago Amarillo", "3", "Ramas"],
        ["PR003", "Jardín Primaveral", "CO001", "Contenedor", "Florero Vidrio Grande", "1", "Unidad"],
        
        # Elegancia Rosa (PR004)
        ["PR004", "Elegancia Rosa", "FL003", "Flor", "Rosa Rosado", "12", "Tallos"],
        ["PR004", "Elegancia Rosa", "FL019", "Flor", "Eucalipto Verde", "4", "Ramas"],
        ["PR004", "Elegancia Rosa", "CO004", "Contenedor", "Florero Cerámica Blanco", "1", "Unidad"],
        
        # Sol Radiante (PR005)
        ["PR005", "Sol Radiante", "FL007", "Flor", "Girasol Amarillo", "5", "Tallos"],
        ["PR005", "Sol Radiante", "FL015", "Flor", "Gerbera Naranja", "3", "Tallos"],
        ["PR005", "Sol Radiante", "FL020", "Flor", "Solidago Amarillo", "5", "Ramas"],
        ["PR005", "Sol Radiante", "CO002", "Contenedor", "Florero Vidrio Mediano", "1", "Unidad"],
        
        # Dulce Lirio (PR006)
        ["PR006", "Dulce Lirio", "FL005", "Flor", "Lirio Blanco", "4", "Tallos"],
        ["PR006", "Dulce Lirio", "FL006", "Flor", "Lirio Rosado", "3", "Tallos"],
        ["PR006", "Dulce Lirio", "FL019", "Flor", "Eucalipto Verde", "3", "Ramas"],
        ["PR006", "Dulce Lirio", "CO001", "Contenedor", "Florero Vidrio Grande", "1", "Unidad"],
        
        # Orquídea Imperial (PR008)
        ["PR008", "Orquídea Imperial", "FL017", "Flor", "Orquídea Blanco", "3", "Tallos"],
        ["PR008", "Orquídea Imperial", "CO007", "Contenedor", "Macetero Cerámica Mediano", "1", "Unidad"],
    ]
    
    for fila in recetas:
        ws.append(fila)
    
    # Ajustar anchos
    ws.column_dimensions['A'].width = 12
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 25
    ws.column_dimensions['F'].width = 18
    ws.column_dimensions['G'].width = 10
    
    wb.save("05_Recetas_Productos.xlsx")
    print("✅ Archivo '05_Recetas_Productos.xlsx' creado")

def crear_proveedores():
    """Crea archivo de proveedores"""
    wb = Workbook()
    ws = wb.active
    ws.title = "Proveedores"
    
    # Encabezados
    headers = ["ID", "Nombre", "Contacto", "Teléfono", "Email", "Especialidad", "Días Entrega", "Notas"]
    ws.append(headers)
    crear_estilo_header(ws)
    
    # Proveedores demo
    proveedores = [
        ["PROV001", "Flores del Valle", "Juan Pérez", "+56987654321", "contacto@floresdelval.cl", "Rosas, Claveles, Gerberas", "Lunes, Miércoles, Viernes", "Entrega temprano"],
        ["PROV002", "Jardín Central", "María Silva", "+56987654322", "ventas@jardincentral.cl", "Lirios, Tulipanes, Orquídeas", "Martes, Jueves", "Flores premium"],
        ["PROV003", "Campo Florido", "Carlos Ramírez", "+56987654323", "info@campoflorido.cl", "Girasoles, Hortensias, Follaje", "Lunes, Jueves", "Productos de temporada"],
        ["PROV004", "Cerámica Artesanal", "Ana Torres", "+56987654324", "ventas@ceramicaarte.cl", "Floreros, Maceteros", "A pedido", "Mínimo 5 unidades"],
        ["PROV005", "Mimbrería Los Andes", "Luis González", "+56987654325", "contacto@mimbreria.cl", "Canastos, Cestas", "A pedido", "Productos artesanales"],
    ]
    
    for fila in proveedores:
        ws.append(fila)
    
    # Ajustar anchos
    ws.column_dimensions['A'].width = 10
    ws.column_dimensions['B'].width = 20
    ws.column_dimensions['C'].width = 18
    ws.column_dimensions['D'].width = 15
    ws.column_dimensions['E'].width = 25
    ws.column_dimensions['F'].width = 30
    ws.column_dimensions['G'].width = 25
    ws.column_dimensions['H'].width = 20
    
    wb.save("06_Proveedores.xlsx")
    print("✅ Archivo '06_Proveedores.xlsx' creado")

if __name__ == "__main__":
    print("\n🌸 Generando archivos Excel demo para Las-Lira...\n")
    
    crear_inventario_flores()
    crear_inventario_contenedores()
    crear_productos_catalogo()
    crear_pedidos()
    crear_recetas_productos()
    crear_proveedores()
    
    print("\n✨ ¡Todos los archivos han sido creados exitosamente!\n")
    print("Archivos generados:")
    print("  1. 01_Inventario_Flores.xlsx")
    print("  2. 02_Inventario_Contenedores.xlsx")
    print("  3. 03_Catalogo_Productos.xlsx")
    print("  4. 04_Pedidos.xlsx")
    print("  5. 05_Recetas_Productos.xlsx")
    print("  6. 06_Proveedores.xlsx")
    print("\n📁 Los archivos están listos para subir a Google Drive")

