#!/bin/bash

echo "🌸 =================================="
echo "   LAS LIRA - Sistema de Gestión"
echo "   =================================="
echo ""
echo "📍 URLs:"
echo "   • Backend:  http://127.0.0.1:5001"
echo "   • Frontend: http://localhost:3001"
echo ""
echo "🚀 Iniciando servidores..."
echo ""

# Terminal 1: Backend
osascript -e 'tell app "Terminal" to do script "cd \"'$(pwd)'/backend\" && echo \"🔧 Iniciando Backend...\" && python3 app.py"'

# Esperar 2 segundos para que el backend inicie primero
sleep 2

# Terminal 2: Frontend
osascript -e 'tell app "Terminal" to do script "cd \"'$(pwd)'/frontend\" && echo \"🎨 Iniciando Frontend...\" && PORT=3001 npm run dev"'

echo "✅ Servidores iniciados en nuevas terminales"
echo ""
echo "💡 Para detener los servidores:"
echo "   Presiona Ctrl+C en cada terminal"
echo ""

