"""
Aplicación principal Flask para Las-Lira
Sistema de gestión de florería
"""

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///laslira.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensiones
CORS(app)
db = SQLAlchemy(app)

# Importar rutas
from routes import (
    pedidos_routes, inventario_routes, productos_routes, 
    upload_routes, rutas_routes, producto_colores_routes
)

# Registrar blueprints
app.register_blueprint(pedidos_routes.bp, url_prefix='/api/pedidos')
app.register_blueprint(inventario_routes.bp, url_prefix='/api/inventario')
app.register_blueprint(productos_routes.bp, url_prefix='/api/productos')
app.register_blueprint(upload_routes.bp, url_prefix='/api/upload')
app.register_blueprint(rutas_routes.bp, url_prefix='/api/rutas')
app.register_blueprint(producto_colores_routes.bp, url_prefix='/api/productos')

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
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
    
    # Ejecutar servidor
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_ENV') == 'development'
    )

