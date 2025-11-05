#!/usr/bin/env python3
"""
Pobla eventos directamente vía API
"""

import requests
import json

API_URL = 'http://localhost:8000/api'

eventos = [
    {
        'cliente_nombre': 'María González',
        'cliente_telefono': '+56912345678',
        'cliente_email': 'maria.gonzalez@email.com',
        'nombre_evento': 'Boda María & Juan',
        'tipo_evento': 'Boda',
        'fecha_evento': '2025-11-15',
        'hora_evento': '18:00',
        'lugar_evento': 'Hotel Plaza, Santiago',
        'cantidad_personas': 150,
        'margen_porcentaje': 30,
        'notas_cotizacion': 'Cliente solicita flores blancas y rosadas',
        'costo_total': 130000,
        'precio_propuesta': 169000
    },
    {
        'cliente_nombre': 'Empresa TechCorp',
        'cliente_telefono': '+56987654321',
        'cliente_email': 'eventos@techcorp.cl',
        'nombre_evento': 'Aniversario 10 años TechCorp',
        'tipo_evento': 'Corporativo',
        'fecha_evento': '2025-12-01',
        'hora_evento': '19:30',
        'lugar_evento': 'Centro de Eventos Espacio Riesco',
        'cantidad_personas': 200,
        'margen_porcentaje': 25,
        'notas_cotizacion': 'Evento corporativo formal, colores azul y blanco',
        'costo_total': 630000,
        'precio_propuesta': 787500
    },
    {
        'cliente_nombre': 'Carolina Pérez',
        'cliente_telefono': '+56923456789',
        'cliente_email': 'caro.perez@gmail.com',
        'nombre_evento': 'Cumpleaños 30 de Carolina',
        'tipo_evento': 'Cumpleaños',
        'fecha_evento': '2025-10-30',
        'hora_evento': '20:00',
        'lugar_evento': 'Restaurant El Jardín, Providencia',
        'cantidad_personas': 80,
        'margen_porcentaje': 35,
        'notas_cotizacion': 'Temática tropical, muchas flores coloridas',
        'costo_total': 250000,
        'precio_propuesta': 337500
    }
]

def poblar():
    print("🌸 POBLANDO EVENTOS VIA API...")
    print("="*60)
    
    for evento in eventos:
        try:
            response = requests.post(f'{API_URL}/eventos', json=evento)
            if response.status_code == 201:
                data = response.json()
                print(f"✅ {data['data']['id']} - {evento['nombre_evento']}")
            else:
                print(f"❌ Error: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("="*60)
    print("✨ Completado!")

if __name__ == '__main__':
    poblar()

