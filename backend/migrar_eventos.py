#!/usr/bin/env python3
"""
Migración para agregar tablas de eventos y columnas cantidad_en_evento
"""

import sys
import os

# Cambiar al directorio del script
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Crear app e inicializar DB
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///floreria.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Importar modelos para que db.create_all() funcione
from models.evento import Evento, EventoInsumo, ProductoEvento

def migrar_eventos():
    """Ejecuta las migraciones necesarias para eventos"""
    
    with app.app_context():
        print("🔄 Iniciando migración de eventos...")
        
        # Agregar cantidad_en_evento a flores
        try:
            with db.engine.connect() as conn:
                conn.execute(text(
                    "ALTER TABLE flores ADD COLUMN cantidad_en_evento INTEGER DEFAULT 0 NOT NULL"
                ))
                conn.commit()
            print("✅ Columna cantidad_en_evento agregada a flores")
        except Exception as e:
            if 'duplicate column' in str(e).lower() or 'already exists' in str(e).lower():
                print("ℹ️  Columna cantidad_en_evento ya existe en flores")
            else:
                print(f"❌ Error en flores: {e}")
        
        # Agregar cantidad_en_evento a contenedores
        try:
            with db.engine.connect() as conn:
                conn.execute(text(
                    "ALTER TABLE contenedores ADD COLUMN cantidad_en_evento INTEGER DEFAULT 0 NOT NULL"
                ))
                conn.commit()
            print("✅ Columna cantidad_en_evento agregada a contenedores")
        except Exception as e:
            if 'duplicate column' in str(e).lower() or 'already exists' in str(e).lower():
                print("ℹ️  Columna cantidad_en_evento ya existe en contenedores")
            else:
                print(f"❌ Error en contenedores: {e}")
        
        # Crear todas las tablas nuevas (eventos, evento_insumos, productos_evento)
        try:
            db.create_all()
            print("✅ Tablas de eventos creadas")
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")
        
        print("✨ Migración completada!")

if __name__ == "__main__":
    migrar_eventos()

