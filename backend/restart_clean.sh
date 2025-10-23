#!/bin/bash

echo "🧹 Limpiando procesos..."
pkill -9 -f "python.*run.py" 2>/dev/null
pkill -9 -f "python.*app.py" 2>/dev/null
pkill -9 -f "python.*simple_run" 2>/dev/null
killall -9 python3 2>/dev/null
sleep 2

echo "🗑️  Limpiando cache..."
cd /Users/juliettegramatges/Las-Lira/backend
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

echo "🗄️  Eliminando BD para recrear..."
rm -f floreria.db

echo "🚀 Iniciando servidor..."
python3 simple_run.py > backend.log 2>&1 &

sleep 3
echo "✅ Servidor iniciado. Ver logs:"
tail -20 backend.log

