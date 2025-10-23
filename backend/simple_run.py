import os
os.chdir('/Users/juliettegramatges/Las-Lira/backend')

from app import app, db

# Crear tablas
with app.app_context():
    db.create_all()
    print("✅ BD OK")

# Run sin reloader
app.run(host='0.0.0.0', port=8000, debug=False)

