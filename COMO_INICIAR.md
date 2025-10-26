# 🌸 Las Lira - Cómo Iniciar el Sistema

## 🚀 Inicio Rápido (1 comando)

```bash
./start.sh
```

Este script abre 2 terminales automáticamente:
- **Terminal 1**: Backend (Flask) en http://127.0.0.1:5001
- **Terminal 2**: Frontend (React + Vite) en http://localhost:3001

---

## 📝 Inicio Manual (2 terminales)

### Terminal 1: Backend
```bash
cd backend
python3 app.py
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

---

## 🌐 URLs del Sistema

| Servicio | URL | Descripción |
|----------|-----|-------------|
| Frontend | http://localhost:3001 | Interfaz de usuario |
| Backend API | http://127.0.0.1:5001 | API REST |
| Health Check | http://127.0.0.1:5001/api/health | Verificar que el backend funciona |

---

## 🛑 Detener los Servidores

Presiona `Ctrl + C` en cada terminal.

---

## 📊 Datos Importados

El sistema ya tiene:
- ✅ **2,857 clientes** históricos
- ✅ **8,686 pedidos** desde 2022
- ✅ **188 productos** del catálogo
- ✅ **129 insumos** (flores, contenedores, follajes)

---

## 🔧 Solución de Problemas

### Backend no inicia
```bash
cd backend
python3 -m pip install -r requirements.txt
python3 app.py
```

### Frontend no inicia
```bash
cd frontend
npm install
npm run dev
```

### Puerto ocupado
Si el puerto 3001 está ocupado, edita `frontend/vite.config.js`:
```javascript
server: {
  port: 3002,  // Cambiar al puerto que quieras
  ...
}
```

---

## 📚 Documentación Adicional

- **Importación de Datos**: Ver `IMPORTACION_DATOS.md`
- **Procesamiento Trello**: Ver `PROCESAMIENTO_TRELLO.md`
- **Estructura Base de Datos**: Ver `DATABASE_DESIGN.md`

