"""
Versión simplificada de la aplicación Flask
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'

# CORS simplificado
CORS(app, resources={r"/*": {"origins": "*"}})

# Ruta a la base de datos
DB_PATH = Path(__file__).parent / 'instance' / 'laslira.db'

def get_db():
    """Obtener conexión a la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/productos', methods=['GET'])
def listar_productos():
    """Listar productos"""
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))
        offset = (page - 1) * limit
        
        conn = get_db()
        cursor = conn.cursor()
        
        # Contar total
        cursor.execute("SELECT COUNT(*) FROM productos WHERE activo = 1")
        total = cursor.fetchone()[0]
        
        # Obtener productos
        cursor.execute("""
            SELECT * FROM productos 
            WHERE activo = 1 
            ORDER BY nombre 
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        productos = []
        for row in cursor.fetchall():
            productos.append({
                'id': row['id'],
                'nombre': row['nombre'],
                'descripcion': row['descripcion'],
                'tipo_arreglo': row['tipo_arreglo'],
                'colores_asociados': row['colores_asociados'],
                'flores_asociadas': row['flores_asociadas'],
                'tipos_macetero': row['tipos_macetero'],
                'precio_venta': float(row['precio_venta']) if row['precio_venta'] else 0,
                'cuidados': row['cuidados'],
                'disponible_shopify': bool(row['disponible_shopify'])
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': productos,
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/inventario/flores', methods=['GET'])
def listar_flores():
    """Listar flores"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM flores ORDER BY nombre")
        
        flores = []
        for row in cursor.fetchall():
            flores.append({
                'id': row['id'],
                'nombre': row['nombre'] or f"{row['tipo']} {row['color'] or ''}".strip(),
                'tipo': row['tipo'],
                'color': row['color'],
                'ubicacion': row['ubicacion'],
                'costo_unitario': float(row['costo_unitario']) if row['costo_unitario'] else 0,
                'cantidad_stock': row['cantidad_stock'],
                'cantidad_en_uso': row['cantidad_en_uso'],
                'cantidad_en_evento': row['cantidad_en_evento'],
                'cantidad_disponible': row['cantidad_stock'] - row['cantidad_en_uso'] - row['cantidad_en_evento']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': flores
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/inventario/contenedores', methods=['GET'])
def listar_contenedores():
    """Listar contenedores"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contenedores ORDER BY nombre")
        
        contenedores = []
        for row in cursor.fetchall():
            contenedores.append({
                'id': row['id'],
                'nombre': row['nombre'],
                'tipo': row['tipo'],
                'ubicacion': row['ubicacion'],
                'costo': float(row['costo']) if row['costo'] else 0,
                'cantidad_stock': row['cantidad_stock'],
                'cantidad_en_uso': row['cantidad_en_uso'],
                'cantidad_en_evento': row['cantidad_en_evento'],
                'cantidad_disponible': row['cantidad_stock'] - row['cantidad_en_uso'] - row['cantidad_en_evento']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': contenedores
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """Ruta principal"""
    return jsonify({
        'app': 'Las-Lira Backend',
        'version': '1.0',
        'status': 'running'
    })

if __name__ == '__main__':
    print("=" * 80)
    print("🌸 LAS-LIRA BACKEND - Versión Simple")
    print("=" * 80)
    print("\n📍 Servidor corriendo en: http://127.0.0.1:5001")
    print("📍 API: http://127.0.0.1:5001/api")
    print("\n⚠️  Presiona CTRL+C para detener\n")
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=5001, debug=False)

