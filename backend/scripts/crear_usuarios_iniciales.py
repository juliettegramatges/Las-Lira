"""
Script para crear usuarios iniciales del sistema
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from extensions import db
from models.usuario import Usuario

def crear_usuarios_iniciales():
    """Crea los usuarios iniciales del sistema"""
    with app.app_context():
        # Verificar si ya existen usuarios
        if Usuario.query.count() > 0:
            print("⚠️  Ya existen usuarios en la base de datos.")
            respuesta = input("¿Deseas crear usuarios adicionales? (s/n): ").lower()
            if respuesta != 's':
                print("❌ Operación cancelada.")
                return
        
        usuarios = [
            {
                'username': 'admin',
                'password': 'admin123',
                'rol': 'admin',
                'nombre': 'Administrador'
            },
            {
                'username': 'secretaria',
                'password': 'secretaria123',
                'rol': 'secretaria',
                'nombre': 'Secretaria'
            },
            {
                'username': 'taller',
                'password': 'taller123',
                'rol': 'taller',
                'nombre': 'Taller'
            }
        ]
        
        creados = 0
        for user_data in usuarios:
            # Verificar si el usuario ya existe
            if Usuario.query.filter_by(username=user_data['username']).first():
                print(f"⚠️  Usuario '{user_data['username']}' ya existe. Omitiendo...")
                continue
            
            usuario = Usuario(
                username=user_data['username'],
                rol=user_data['rol'],
                nombre=user_data['nombre'],
                activo=True
            )
            usuario.set_password(user_data['password'])
            
            db.session.add(usuario)
            creados += 1
            print(f"✅ Usuario '{user_data['username']}' ({user_data['rol']}) creado exitosamente")
        
        if creados > 0:
            db.session.commit()
            print(f"\n🎉 {creados} usuario(s) creado(s) exitosamente")
            print("\n📋 Credenciales:")
            print("   Admin:      admin / admin123")
            print("   Secretaria: secretaria / secretaria123")
            print("   Taller:     taller / taller123")
        else:
            print("\n❌ No se crearon nuevos usuarios.")

if __name__ == '__main__':
    crear_usuarios_iniciales()

