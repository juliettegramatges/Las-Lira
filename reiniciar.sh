#!/bin/bash

echo "🔄 =================================="
echo "   REINICIANDO LAS LIRA"
echo "   =================================="
echo ""

# Matar procesos existentes
echo "🛑 Deteniendo servidores anteriores..."
pkill -f "python3 app.py" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 1

echo "✅ Servidores detenidos"
echo ""
echo "🚀 Iniciando nuevos servidores..."
echo ""

# Terminal 1: Backend
osascript -e 'tell app "Terminal" to do script "cd \"'$(pwd)'/backend\" && echo \"🔧 Backend - http://127.0.0.1:5000\" && python3 app.py"'

# Esperar 3 segundos
sleep 3

# Terminal 2: Frontend  
osascript -e 'tell app "Terminal" to do script "cd \"'$(pwd)'/frontend\" && echo \"🎨 Frontend - http://localhost:3001\" && npm run dev"'

echo "✅ Servidores reiniciados"
echo ""
echo "📍 URLs:"
echo "   • Frontend: http://localhost:3001"
echo "   • Backend:  http://127.0.0.1:5000"
echo "   • Health:   http://127.0.0.1:5000/api/health"
echo ""


