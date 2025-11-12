
"""
Aplicación principal Flask para Las-Lira
Sistema de gestión de florería
"""

from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from extensions import db

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Deshabilitar redirecciones automáticas por trailing slash (evita problemas con CORS preflight)
app.url_map.strict_slashes = False

# Configurar ruta correcta de la base de datos
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', f'sqlite:///{os.path.join(basedir, "instance", "laslira.db")}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensiones
# Configurar CORS para permitir requests desde el frontend
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:3001",
            "http://localhost:3002", 
            "http://localhost:5173", 
            "http://127.0.0.1:3001",
            "http://127.0.0.1:3002",
            "http://127.0.0.1:5001"
        ],
        "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})
db.init_app(app)

# Importar rutas
from routes import (
    clientes_routes,
    pedidos_routes, inventario_routes, productos_routes,
    upload_routes, rutas_routes, producto_colores_routes,
    pedido_insumos_routes, evento_routes, exportar_routes,
    analisis_routes, reportes_routes
)

# Registrar blueprints
app.register_blueprint(clientes_routes.bp, url_prefix='/api/clientes')
app.register_blueprint(pedidos_routes.bp, url_prefix='/api/pedidos')
app.register_blueprint(pedido_insumos_routes.bp)  # Ya tiene su propio prefix definido
app.register_blueprint(inventario_routes.bp, url_prefix='/api/inventario')
app.register_blueprint(productos_routes.bp, url_prefix='/api/productos')
app.register_blueprint(upload_routes.bp, url_prefix='/api/upload')
app.register_blueprint(rutas_routes.bp, url_prefix='/api/rutas')
app.register_blueprint(producto_colores_routes.bp, url_prefix='/api/productos-colores')
app.register_blueprint(evento_routes.bp, url_prefix='/api/eventos')
app.register_blueprint(exportar_routes.bp, url_prefix='/api/exportar')
app.register_blueprint(analisis_routes.bp)  # Ya tiene su propio prefix definido (/api/analisis)
app.register_blueprint(reportes_routes.bp, url_prefix='/api/reportes')

@app.route('/')
def index():
    return jsonify({'app': 'Las-Lira Backend', 'status': 'running', 'version': '1.0'})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar que el servidor esté funcionando"""
    return jsonify({
        'status': 'ok',
        'message': 'Las-Lira API funcionando correctamente 🌸'
    })

@app.route('/api', methods=['GET'])
def api_info():
    """Información general de la API"""
    return jsonify({
        'nombre': 'Las-Lira API',
        'version': '1.0.0',
        'descripcion': 'Sistema de gestión integral para florería',
        'endpoints': {
            'pedidos': '/api/pedidos',
            'inventario': '/api/inventario',
            'productos': '/api/productos',
            'rutas': '/api/rutas',
            'health': '/api/health'
        }
    })

if __name__ == '__main__':
    print("=" * 80)
    print("🌸 LAS-LIRA BACKEND")
    print("=" * 80)
    print(f"\n📍 Servidor: http://127.0.0.1:5001")
    print(f"📍 API: http://127.0.0.1:5001/api")
    print(f"\n⚠️  Presiona CTRL+C para detener\n")
    print("=" * 80)
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
    
    # Ejecutar servidor
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5001)),
        debug=False
    )
