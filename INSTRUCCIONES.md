# 🌸 Instrucciones de Instalación y Uso - Las-Lira

## 📦 Requisitos Previos

- Python 3.9 o superior
- Node.js 18 o superior
- npm o yarn

## 🚀 Instalación

### 1. Backend (Flask)

```bash
# Navegar a la carpeta raíz del proyecto
cd Las-Lira

# Crear entorno virtual de Python
python3 -m venv venv

# Activar entorno virtual
# En macOS/Linux:
source venv/bin/activate
# En Windows:
# venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Copiar archivo de configuración
cp backend/env.example backend/.env

# Editar backend/.env con tus configuraciones (opcional por ahora)
```

### 2. Frontend (React + Vite)

```bash
# Navegar a la carpeta frontend
cd frontend

# Instalar dependencias
npm install

# Volver a la raíz
cd ..
```

## ▶️ Ejecutar la Aplicación

### Opción 1: Ejecutar Backend y Frontend por separado

#### Terminal 1 - Backend:
```bash
cd Las-Lira
source venv/bin/activate  # Activar entorno virtual
python backend/app.py
```
El backend estará en: http://localhost:5000

#### Terminal 2 - Frontend:
```bash
cd Las-Lira/frontend
npm run dev
```
El frontend estará en: http://localhost:3000

### Opción 2: Script automatizado (próximamente)

## 📊 Cargar Datos Demo

Los archivos Excel con datos demo ya están creados. Para importarlos a la base de datos:

```bash
# Asegúrate de estar en el entorno virtual activado
python scripts/import_excel_data.py
```

## 🗄️ Base de Datos

La primera vez que ejecutes `python backend/app.py`, se creará automáticamente una base de datos SQLite en `backend/laslira.db`.

### Crear tablas manualmente (opcional):

```bash
cd backend
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

## 📁 Estructura del Proyecto

```
Las-Lira/
├── backend/                 # API Flask
│   ├── app.py              # Aplicación principal
│   ├── models/             # Modelos de datos
│   ├── routes/             # Rutas/Endpoints
│   ├── services/           # Lógica de negocio
│   └── .env                # Configuración (crear desde env.example)
├── frontend/               # Aplicación React
│   ├── src/
│   │   ├── components/     # Componentes React
│   │   ├── pages/          # Páginas
│   │   ├── services/       # API client
│   │   └── main.jsx        # Entrada principal
│   └── package.json
├── *.xlsx                  # Archivos Excel demo
├── requirements.txt        # Dependencias Python
└── README.md              # Documentación principal
```

## 🎯 Funcionalidades Principales

### 1. Tablero Kanban (http://localhost:3000/tablero)
- Vista de pedidos organizados por estado
- Drag & drop para cambiar estados
- Estados: Recibido → En Preparación → Listo → Despachado

### 2. Gestión de Pedidos (http://localhost:3000/pedidos)
- Lista completa de pedidos
- Filtros por estado y canal
- Crear nuevo pedido

### 3. Inventario (http://localhost:3000/inventario)
- Control de flores y contenedores
- Alertas de stock bajo
- Resumen de valor total

### 4. Catálogo de Productos (http://localhost:3000/productos)
- Productos predefinidos para Shopify
- Recetas de cada producto
- Verificación de stock disponible

## 🔧 API Endpoints

### Pedidos
- `GET /api/pedidos` - Listar pedidos
- `GET /api/pedidos/:id` - Obtener pedido
- `POST /api/pedidos` - Crear pedido
- `PATCH /api/pedidos/:id/estado` - Actualizar estado
- `GET /api/pedidos/tablero` - Obtener tablero Kanban

### Inventario
- `GET /api/inventario/flores` - Listar flores
- `GET /api/inventario/contenedores` - Listar contenedores
- `PATCH /api/inventario/flores/:id/stock` - Actualizar stock
- `GET /api/inventario/resumen` - Resumen de inventario

### Productos
- `GET /api/productos` - Listar productos
- `GET /api/productos/:id` - Obtener producto
- `GET /api/productos/:id/verificar-stock` - Verificar disponibilidad
- `POST /api/productos/estimar-costo` - Estimar costo (WhatsApp)

## 📝 Flujo de Trabajo

### Flujo Shopify:
1. Cliente hace pedido en Shopify
2. Pedido se registra como "Recibido"
3. Sistema verifica stock automáticamente
4. Florista mueve pedido a "En Preparación"
5. Sistema descuenta stock automáticamente
6. Pedido avanza: Listo → Despachado → Entregado

### Flujo WhatsApp:
1. Cliente solicita arreglo personalizado
2. Florista usa estimador de costos
3. Se crea pedido con descripción personalizada
4. Al preparar: florista selecciona insumos específicos
5. Sistema descuenta stock
6. Pedido sigue flujo normal

## 🔑 Características del Sistema

### ✅ Control de Inventario
- Descuento automático al preparar pedidos
- Alertas de stock bajo
- Gestión de 2 bodegas
- Tracking de costos

### ✅ Gestión de Pedidos
- Múltiples canales (Shopify, WhatsApp)
- Tablero visual tipo Trello
- Historial de estados
- Información detallada de clientes

### ✅ Productos Flexibles
- Productos definidos por color, no por flor específica
- Recetas adaptables a temporada
- Verificación automática de stock
- Estimación de costos para personalizados

## 🐛 Solución de Problemas

### Error: "Module not found"
```bash
# Reinstalar dependencias
pip install -r requirements.txt
# o
npm install
```

### Error: "Port already in use"
```bash
# Cambiar puerto en backend/.env
PORT=5001

# O en frontend/vite.config.js
server: { port: 3001 }
```

### Error de base de datos
```bash
# Eliminar y recrear
rm backend/laslira.db
python backend/app.py  # Se creará automáticamente
```

## 📧 Próximos Pasos

1. Configurar integración con Shopify API
2. Implementar autenticación de usuarios
3. Agregar módulo de reportes
4. Integración con WhatsApp Business API
5. Sincronización con Google Drive para archivos Excel

## 💡 Consejos

- Los archivos Excel demo sirven como backup y para compartir con el equipo
- Puedes exportar datos de la base de datos a Excel en cualquier momento
- El sistema está diseñado para crecer con tu negocio
- Todos los costos se calculan automáticamente

---

**¿Necesitas ayuda?** Revisa el archivo README.md o la documentación en DATABASE_DESIGN.md

