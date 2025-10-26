"""
Aplicación Flask minimalista - Version estable
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

# Inicializar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/laslira.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Inicializar DB
db = SQLAlchemy(app)

# Definir modelos mínimos inline
class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.String(10), primary_key=True)
    nombre = db.Column(db.String(100))
    descripcion = db.Column(db.Text)
    tipo_arreglo = db.Column(db.String(50))
    colores_asociados = db.Column(db.String(300))
    flores_asociadas = db.Column(db.String(300))
    tipos_macetero = db.Column(db.String(200))
    precio_venta = db.Column(db.Numeric(10, 2))
    cuidados = db.Column(db.Text)
    disponible_shopify = db.Column(db.Boolean)
    activo = db.Column(db.Boolean)

class Flor(db.Model):
    __tablename__ = 'flores'
    id = db.Column(db.String(10), primary_key=True)
    nombre = db.Column(db.String(100))
    tipo = db.Column(db.String(50))
    color = db.Column(db.String(30))
    ubicacion = db.Column(db.String(100))
    costo_unitario = db.Column(db.Numeric(10, 2))
    cantidad_stock = db.Column(db.Integer)
    cantidad_en_uso = db.Column(db.Integer)
    cantidad_en_evento = db.Column(db.Integer)

class Contenedor(db.Model):
    __tablename__ = 'contenedores'
    id = db.Column(db.String(10), primary_key=True)
    nombre = db.Column(db.String(100))
    tipo = db.Column(db.String(50))
    ubicacion = db.Column(db.String(100))
    costo = db.Column(db.Numeric(10, 2))
    cantidad_stock = db.Column(db.Integer)
    cantidad_en_uso = db.Column(db.Integer)
    cantidad_en_evento = db.Column(db.Integer)

# Rutas
@app.route('/')
def index():
    return jsonify({'app': 'Las-Lira Backend', 'status': 'running'})

@app.route('/api/productos', methods=['GET'])
def listar_productos():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 100))
        
        query = Producto.query.filter_by(activo=True)
        total = query.count()
        
        productos = query.order_by(Producto.nombre).limit(limit).offset((page - 1) * limit).all()
        
        return jsonify({
            'success': True,
            'data': [{
                'id': p.id,
                'nombre': p.nombre,
                'descripcion': p.descripcion,
                'tipo_arreglo': p.tipo_arreglo,
                'colores_asociados': p.colores_asociados,
                'flores_asociadas': p.flores_asociadas,
                'tipos_macetero': p.tipos_macetero,
                'precio_venta': float(p.precio_venta) if p.precio_venta else 0,
                'cuidados': p.cuidados,
                'disponible_shopify': bool(p.disponible_shopify)
            } for p in productos],
            'total': total,
            'page': page,
            'limit': limit,
            'total_pages': (total + limit - 1) // limit
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/inventario/flores', methods=['GET'])
def listar_flores():
    try:
        flores = Flor.query.order_by(Flor.nombre).all()
        return jsonify({
            'success': True,
            'data': [{
                'id': f.id,
                'nombre': f.nombre or f"{f.tipo} {f.color or ''}".strip(),
                'tipo': f.tipo,
                'color': f.color,
                'ubicacion': f.ubicacion,
                'costo_unitario': float(f.costo_unitario) if f.costo_unitario else 0,
                'cantidad_stock': f.cantidad_stock,
                'cantidad_en_uso': f.cantidad_en_uso,
                'cantidad_en_evento': f.cantidad_en_evento,
                'cantidad_disponible': f.cantidad_stock - f.cantidad_en_uso - f.cantidad_en_evento
            } for f in flores]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/inventario/contenedores', methods=['GET'])
def listar_contenedores():
    try:
        contenedores = Contenedor.query.order_by(Contenedor.nombre).all()
        return jsonify({
            'success': True,
            'data': [{
                'id': c.id,
                'nombre': c.nombre,
                'tipo': c.tipo,
                'ubicacion': c.ubicacion,
                'costo': float(c.costo) if c.costo else 0,
                'cantidad_stock': c.cantidad_stock,
                'cantidad_en_uso': c.cantidad_en_uso,
                'cantidad_en_evento': c.cantidad_en_evento,
                'cantidad_disponible': c.cantidad_stock - c.cantidad_en_uso - c.cantidad_en_evento
            } for c in contenedores]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 80)
    print("🌸 LAS-LIRA BACKEND")
    print("=" * 80)
    print("\n📍 Servidor: http://127.0.0.1:5001")
    print("📍 API: http://127.0.0.1:5001/api")
    print("\n⚠️  Presiona CTRL+C para detener\n")
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=5001, debug=False)


