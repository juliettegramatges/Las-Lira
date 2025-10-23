"""
Script de inicio para el backend de Las-Lira
Configura el PYTHONPATH correctamente antes de ejecutar la aplicación
"""

import sys
import os

# Agregar el directorio raíz al PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Ahora importar y ejecutar la aplicación
from backend.app import app, db

if __name__ == '__main__':
    print("🌸 Iniciando servidor Las-Lira...")
    print(f"📁 Directorio de trabajo: {os.getcwd()}")
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
        print("✅ Base de datos inicializada")
    
    # Ejecutar servidor
    puerto = int(os.getenv('PORT', 8000))
    print(f"🚀 Servidor corriendo en http://localhost:{puerto}")
    app.run(
        host='0.0.0.0',
        port=puerto,
        debug=os.getenv('FLASK_ENV', 'development') == 'development'
    )

