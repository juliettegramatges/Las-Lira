#!/usr/bin/env python3
"""
Genera Excel demo con estructura de eventos
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from datetime import datetime, timedelta

def crear_excel_eventos():
    """Crea Excel con datos demo de eventos"""
    
    wb = openpyxl.Workbook()
    
    # ========================================
    # HOJA 1: EVENTOS
    # ========================================
    ws_eventos = wb.active
    ws_eventos.title = "01_Eventos"
    
    headers_eventos = [
        'ID Evento',
        'Cliente Nombre',
        'Cliente Teléfono',
        'Cliente Email',
        'Nombre Evento',
        'Tipo Evento',
        'Fecha Evento',
        'Hora Evento',
        'Lugar Evento',
        'Cantidad Personas',
        'Estado',
        'Costo Insumos',
        'Costo Mano Obra',
        'Costo Transporte',
        'Costo Otros',
        'Costo Total',
        'Margen %',
        'Precio Propuesta',
        'Precio Final',
        'Anticipo',
        'Saldo',
        'Pagado',
        'Insumos Reservados',
        'Insumos Descontados',
        'Insumos Faltantes',
        'Notas Cotización',
        'Fecha Cotización'
    ]
    
    ws_eventos.append(headers_eventos)
    
    # Estilo headers
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    
    for cell in ws_eventos[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Datos demo
    hoy = datetime.now()
    
    datos_eventos = [
        # Evento 1: Boda
        [
            'EV001',
            'Sofía Martínez',
            '+569 8765 4321',
            'sofia.martinez@email.com',
            'Boda Sofía & Diego',
            'Boda',
            (hoy + timedelta(days=45)).strftime('%Y-%m-%d'),
            '18:00',
            'Parque Araucano - Santiago',
            150,
            'Confirmado',
            850000,
            300000,
            50000,
            100000,
            1300000,
            35,
            1755000,
            1755000,
            500000,
            1255000,
            False,
            True,
            False,
            False,
            'Boda de jardín, requiere arreglos florales grandes',
            hoy.strftime('%Y-%m-%d')
        ],
        # Evento 2: Cumpleaños
        [
            'EV002',
            'Roberto Silva',
            '+569 1234 5678',
            'roberto.silva@email.com',
            'Cumpleaños 50 años Roberto',
            'Cumpleaños',
            (hoy + timedelta(days=20)).strftime('%Y-%m-%d'),
            '20:00',
            'Salón Los Pinos',
            80,
            'Propuesta Enviada',
            380000,
            150000,
            30000,
            40000,
            600000,
            30,
            780000,
            0,
            0,
            0,
            False,
            False,
            False,
            False,
            'Centro de mesa elegantes, colores dorado y blanco',
            hoy.strftime('%Y-%m-%d')
        ],
        # Evento 3: Corporativo
        [
            'EV003',
            'Empresa TechCorp',
            '+562 2345 6789',
            'eventos@techcorp.cl',
            'Aniversario 10 años TechCorp',
            'Corporativo',
            (hoy + timedelta(days=60)).strftime('%Y-%m-%d'),
            '19:00',
            'Hotel W Santiago',
            200,
            'Cotización',
            1200000,
            450000,
            80000,
            150000,
            1880000,
            40,
            2632000,
            0,
            0,
            0,
            False,
            False,
            False,
            False,
            'Evento corporativo formal, colores azul y plata',
            hoy.strftime('%Y-%m-%d')
        ]
    ]
    
    for fila in datos_eventos:
        ws_eventos.append(fila)
    
    # Ajustar anchos
    anchos = {'A': 12, 'B': 20, 'C': 18, 'D': 25, 'E': 30, 'F': 15, 'G': 15, 'H': 12,
              'I': 30, 'J': 15, 'K': 18, 'L': 15, 'M': 18, 'N': 15, 'O': 12, 'P': 15,
              'Q': 12, 'R': 18, 'S': 15, 'T': 12, 'U': 12, 'V': 10, 'W': 18, 'X': 18,
              'Y': 18, 'Z': 40, 'AA': 18}
    
    for col, width in anchos.items():
        ws_eventos.column_dimensions[col].width = width
    
    # ========================================
    # HOJA 2: INSUMOS DE EVENTOS
    # ========================================
    ws_insumos = wb.create_sheet("02_Insumos_Eventos")
    
    headers_insumos = [
        'ID Evento',
        'Tipo Insumo',
        'ID Insumo',
        'Nombre',
        'Cantidad',
        'Costo Unitario',
        'Costo Total',
        'Reservado',
        'Descontado',
        'Devuelto',
        'Cantidad Faltante',
        'Notas'
    ]
    
    ws_insumos.append(headers_insumos)
    
    for cell in ws_insumos[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Datos insumos
    datos_insumos = [
        # Evento 1 - Boda
        ['EV001', 'producto', 'PR001', 'Passion Roja (15 arreglos)', 15, 25000, 375000, True, False, False, 0, 'Centros de mesa'],
        ['EV001', 'producto', 'PR006', 'Dulce Lirio (10 arreglos)', 10, 55000, 550000, True, False, False, 0, 'Arreglos altar'],
        ['EV001', 'producto_evento', 'PE001', 'Mantel Blanco 3x3m', 20, 8000, 160000, True, False, False, 0, 'Para mesas'],
        ['EV001', 'producto_evento', 'PE005', 'Vela Pilar Grande', 30, 3000, 90000, True, False, False, 0, 'Iluminación'],
        ['EV001', 'contenedor', 'CT003', 'Florero Vidrio Grande', 25, 5000, 125000, True, False, False, 0, 'Para centros de mesa'],
        
        # Evento 2 - Cumpleaños
        ['EV002', 'producto', 'PR004', 'Elegancia Rosa (12 arreglos)', 12, 35000, 420000, False, False, False, 0, 'Decoración mesas'],
        ['EV002', 'producto_evento', 'PE002', 'Mantel Dorado 2.5x2.5m', 10, 10000, 100000, False, False, False, 0, 'Mesas principales'],
        ['EV002', 'producto_evento', 'PE006', 'Vela Flotante', 50, 1500, 75000, False, False, False, 0, 'Ambiente'],
        
        # Evento 3 - Corporativo
        ['EV003', 'producto', 'PR009', 'Ramo Clásico (30 arreglos)', 30, 50000, 1500000, False, False, False, 0, 'Centros de mesa'],
        ['EV003', 'producto_evento', 'PE003', 'Mantel Azul 3x3m', 25, 9000, 225000, False, False, False, 0, 'Mesas corporativas'],
        ['EV003', 'producto_evento', 'PE007', 'Camino de Mesa Plateado', 25, 5000, 125000, False, False, False, 0, 'Decoración'],
    ]
    
    for fila in datos_insumos:
        ws_insumos.append(fila)
    
    # Ajustar anchos
    ws_insumos.column_dimensions['A'].width = 12
    ws_insumos.column_dimensions['B'].width = 18
    ws_insumos.column_dimensions['C'].width = 12
    ws_insumos.column_dimensions['D'].width = 35
    ws_insumos.column_dimensions['E'].width = 10
    ws_insumos.column_dimensions['F'].width = 15
    ws_insumos.column_dimensions['G'].width = 15
    ws_insumos.column_dimensions['H'].width = 12
    ws_insumos.column_dimensions['I'].width = 12
    ws_insumos.column_dimensions['J'].width = 12
    ws_insumos.column_dimensions['K'].width = 15
    ws_insumos.column_dimensions['L'].width = 30
    
    # ========================================
    # HOJA 3: PRODUCTOS DE EVENTOS
    # ========================================
    ws_productos_evento = wb.create_sheet("03_Productos_Evento")
    
    headers_productos = [
        'Código',
        'Nombre',
        'Categoría',
        'Stock',
        'En Evento',
        'Disponible',
        'Costo Compra',
        'Costo Alquiler',
        'Descripción',
        'Medidas',
        'Color',
        'Material'
    ]
    
    ws_productos_evento.append(headers_productos)
    
    for cell in ws_productos_evento[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    # Datos productos de eventos
    datos_productos_evento = [
        # Mantelería
        ['PE001', 'Mantel Blanco 3x3m', 'Mantelería', 30, 20, 10, 8000, 3000, 'Mantel blanco para mesas cuadradas', '3x3 metros', 'Blanco', 'Poliéster'],
        ['PE002', 'Mantel Dorado 2.5x2.5m', 'Mantelería', 15, 0, 15, 10000, 4000, 'Mantel dorado elegante', '2.5x2.5 metros', 'Dorado', 'Satén'],
        ['PE003', 'Mantel Azul 3x3m', 'Mantelería', 20, 0, 20, 9000, 3500, 'Mantel azul corporativo', '3x3 metros', 'Azul', 'Poliéster'],
        ['PE004', 'Camino de Mesa Blanco', 'Mantelería', 40, 0, 40, 3000, 1500, 'Camino de mesa decorativo', '3x0.5 metros', 'Blanco', 'Lino'],
        
        # Iluminación
        ['PE005', 'Vela Pilar Grande', 'Iluminación', 100, 30, 70, 3000, 0, 'Vela pilar decorativa grande', '15cm alto x 10cm diámetro', 'Blanco', 'Cera'],
        ['PE006', 'Vela Flotante', 'Iluminación', 200, 0, 200, 1500, 0, 'Velas pequeñas flotantes', '5cm diámetro', 'Blanco', 'Cera'],
        ['PE007', 'Camino de Mesa Plateado', 'Mantelería', 30, 0, 30, 5000, 2000, 'Camino con detalles plateados', '3x0.5 metros', 'Plateado', 'Satén'],
        
        # Mobiliario
        ['PE008', 'Triángulo Floral Grande', 'Decoración', 10, 0, 10, 45000, 15000, 'Estructura triangular para arreglos', '2m altura', 'Dorado', 'Metal'],
        ['PE009', 'Arco Floral Redondo', 'Decoración', 5, 0, 5, 80000, 25000, 'Arco circular para bodas', '2.5m diámetro', 'Blanco', 'Metal'],
        ['PE010', 'Base Cilíndrica Grande', 'Decoración', 15, 0, 15, 25000, 8000, 'Cilindro decorativo alto', '1m altura x 30cm diámetro', 'Transparente', 'Acrílico'],
        
        # Otros
        ['PE011', 'Servilleta Lino Blanca', 'Mantelería', 200, 0, 200, 1500, 500, 'Servilleta de lino premium', '45x45cm', 'Blanco', 'Lino'],
        ['PE012', 'Centro de Mesa Espejo', 'Decoración', 25, 0, 25, 4000, 1500, 'Espejo redondo decorativo', '30cm diámetro', 'Espejo', 'Vidrio'],
    ]
    
    for fila in datos_productos_evento:
        ws_productos_evento.append(fila)
    
    # Ajustar anchos
    for col, width in [('A', 10), ('B', 30), ('C', 15), ('D', 8), ('E', 10), ('F', 12),
                       ('G', 14), ('H', 14), ('I', 40), ('J', 20), ('K', 12), ('L', 12)]:
        ws_productos_evento.column_dimensions[col].width = width
    
    # ========================================
    # HOJA 4: INSTRUCCIONES
    # ========================================
    ws_instrucciones = wb.create_sheet("📖 INSTRUCCIONES")
    
    instrucciones = [
        ['SISTEMA DE GESTIÓN DE EVENTOS'],
        [''],
        ['Este archivo contiene la estructura de datos para eventos de Las-Lira.'],
        [''],
        ['📋 HOJA 1: EVENTOS'],
        ['- Lista de todos los eventos con sus estados y costos'],
        ['- Estados: Cotización → Propuesta → Confirmado → En Preparación → En Evento → Finalizado → Retirado'],
        ['- Costos separados: insumos, mano de obra, transporte, otros'],
        ['- Margen % para calcular precio de venta'],
        ['- Control de pagos: anticipo, saldo, pagado'],
        ['- Control de insumos: reservados, descontados, faltantes'],
        [''],
        ['📦 HOJA 2: INSUMOS DE EVENTOS'],
        ['- Cada evento tiene múltiples insumos'],
        ['- Tipos: flor, contenedor, producto, producto_evento, otro'],
        ['- Control individual: cantidad, costo, reservado, descontado, devuelto'],
        ['- Cantidad faltante: lo que no se devolvió'],
        [''],
        ['🎨 HOJA 3: PRODUCTOS DE EVENTOS'],
        ['- Productos específicos para eventos (manteles, velas, triángulos, etc)'],
        ['- Categorías: Mantelería, Iluminación, Decoración, Mobiliario'],
        ['- Stock separado de flores y contenedores normales'],
        ['- Costo compra vs costo alquiler'],
        ['- Control de "En Evento" para reservas'],
        [''],
        ['🔄 FLUJO DE TRABAJO:'],
        [''],
        ['1. COTIZACIÓN:'],
        ['   • Crear evento con datos del cliente'],
        ['   • Agregar insumos necesarios'],
        ['   • Calcular costos'],
        ['   • Definir margen deseado'],
        ['   • Estado: "Cotización"'],
        [''],
        ['2. PROPUESTA:'],
        ['   • Revisar cotización'],
        ['   • Ajustar márgenes si es necesario'],
        ['   • Generar presupuesto (PDF/Excel)'],
        ['   • Enviar al cliente'],
        ['   • Estado: "Propuesta Enviada"'],
        [''],
        ['3. CONFIRMACIÓN:'],
        ['   • Cliente acepta'],
        ['   • Confirmar fecha del evento'],
        ['   • RESERVAR INSUMOS (cantidad_en_evento++)'],
        ['   • No descuenta stock todavía'],
        ['   • Solicitar anticipo'],
        ['   • Estado: "Confirmado"'],
        [''],
        ['4. PREPARACIÓN:'],
        ['   • Opción: descontar stock ahora o al finalizar'],
        ['   • Preparar insumos'],
        ['   • Coordinar logística'],
        ['   • Estado: "En Preparación"'],
        [''],
        ['5. EVENTO:'],
        ['   • Día del evento'],
        ['   • Insumos en uso'],
        ['   • Estado: "En Evento"'],
        [''],
        ['6. FINALIZADO:'],
        ['   • Evento terminó'],
        ['   • Presionar "Evento Finalizado"'],
        ['   • Estado: "Finalizado"'],
        [''],
        ['7. RETIRO:'],
        ['   • Recoger insumos'],
        ['   • CHEQUEAR QUÉ VOLVIÓ Y QUÉ NO'],
        ['   • Marcar devuelto o faltante'],
        ['   • Si hay faltantes:'],
        ['     - Agregar a lista_faltantes'],
        ['     - Marcar insumos_faltantes = True'],
        ['     - Marcar cliente con "Insumo faltante en evento"'],
        ['   • Liberar insumos (cantidad_en_evento--)'],
        ['   • Estado: "Retirado"'],
        [''],
        ['💡 CARACTERÍSTICAS ESPECIALES:'],
        [''],
        ['CONTROL DE STOCK SEPARADO:'],
        ['• Flores: cantidad_stock - cantidad_en_uso - cantidad_en_evento = disponible'],
        ['• Contenedores: stock - en_uso - en_evento = disponible'],
        ['• Productos Evento: stock - en_evento = disponible'],
        [''],
        ['MARCADORES DE CLIENTE:'],
        ['• Si insumos_faltantes = True → cliente marcado'],
        ['• Útil para decidir si trabajar con ese cliente de nuevo'],
        [''],
        ['FLEXIBILIDAD:'],
        ['• Puedes descontar stock al confirmar O al finalizar'],
        ['• Puedes modificar cotización hasta confirmar'],
        ['• Puedes agregar insumos durante el evento'],
        [''],
        [f'Generado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'],
    ]
    
    for fila in instrucciones:
        ws_instrucciones.append(fila)
    
    ws_instrucciones['A1'].font = Font(bold=True, size=16, color="4472C4")
    ws_instrucciones.column_dimensions['A'].width = 90
    
    # Guardar
    filename = 'ESTRUCTURA_EVENTOS.xlsx'
    wb.save(filename)
    print(f"✅ Excel generado: {filename}")
    print(f"\n📋 Contenido:")
    print(f"   • Hoja 1: 01_Eventos (3 eventos demo)")
    print(f"   • Hoja 2: 02_Insumos_Eventos (insumos por evento)")
    print(f"   • Hoja 3: 03_Productos_Evento (12 productos específicos)")
    print(f"   • Hoja 4: 📖 INSTRUCCIONES (flujo completo)")
    print(f"\n🎯 Tipos de Eventos Demo:")
    print(f"   • EV001: Boda (150 personas, confirmado)")
    print(f"   • EV002: Cumpleaños (80 personas, propuesta)")
    print(f"   • EV003: Corporativo (200 personas, cotización)")
    print(f"\n📦 Productos Evento:")
    print(f"   • Mantelería (manteles, caminos de mesa, servilletas)")
    print(f"   • Iluminación (velas pilar, flotantes)")
    print(f"   • Decoración (triángulos, arcos, bases, espejos)")

if __name__ == "__main__":
    crear_excel_eventos()

