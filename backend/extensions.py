"""
Extensiones de Flask
Inicializa las extensiones sin la app para evitar importaciones circulares
"""

from flask_sqlalchemy import SQLAlchemy

# Inicializar extensiones sin app
db = SQLAlchemy()

