# 🚀 Guía de Inicio Rápido - Las Lira

## ¿Qué tipo de aplicación es?

**Las-Lira es una aplicación web** que se ejecuta en tu navegador. Consta de:
- **Backend (API)**: Servidor Python Flask en `http://localhost:5000`
- **Frontend (Interfaz)**: Aplicación React en `http://localhost:5173`

## 📋 Requisitos Previos

Antes de empezar, asegúrate de tener instalado:
- **Python 3.9+** (verifica con `python3 --version`)
- **Node.js 18+** y npm (verifica con `node --version`)

## 🎬 Instrucciones Paso a Paso

### Paso 1: Instalar Dependencias del Backend

Abre una terminal en el directorio del proyecto y ejecuta:

```bash
# Instalar dependencias de Python
python3 -m pip install -r backend/requirements.txt
```

### Paso 2: Instalar Dependencias del Frontend

En la misma terminal o una nueva:

```bash
# Ir a la carpeta frontend
cd frontend

# Instalar dependencias de Node
npm install

# Volver al directorio raíz
cd ..
```

### Paso 3: Iniciar el Backend (Terminal 1)

En una terminal, ejecuta:

```bash
# Desde el directorio raíz del proyecto
cd backend
python3 app.py
```

Deberías ver algo como:
```
 * Running on http://127.0.0.1:5000
 * Running on http://0.0.0.0:5000
```

✅ **Deja esta terminal abierta** (el servidor debe seguir corriendo)

### Paso 4: Iniciar el Frontend (Terminal 2)

Abre una **segunda terminal** y ejecuta:

```bash
# Desde el directorio raíz del proyecto
cd frontend
npm run dev
```

Deberías ver algo como:
```
  VITE v5.0.8  ready in 1234 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

✅ **Deja esta terminal abierta también**

### Paso 5: Abrir en el Navegador

Abre tu navegador (Chrome, Firefox, Safari, etc.) y ve a:

🌐 **http://localhost:5173**

¡Ya deberías ver la aplicación Las-Lira corriendo! 🌸

## 📱 Navegación en la Aplicación

Una vez abierta, verás un menú lateral con las siguientes secciones:

1. **🏠 Dashboard**: Vista general (en desarrollo)
2. **📦 Inventario**: Gestión de flores y contenedores
3. **🛍️ Pedidos**: Crear y gestionar pedidos
4. **🎨 Productos**: Catálogo de arreglos
5. **📋 Tablero**: Vista Kanban estilo Trello
6. **🚗 Rutas**: **← ¡NUEVA!** Optimización de entregas por comuna

## ⚠️ Solución de Problemas

### El backend no inicia
```bash
# Verifica que tengas Python 3.9+
python3 --version

# Reinstala las dependencias
python3 -m pip install -r backend/requirements.txt --upgrade
```

### El frontend no inicia
```bash
# Verifica que tengas Node.js 18+
node --version

# Limpia e reinstala
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Error "port 5000 already in use"
```bash
# Encuentra el proceso usando el puerto 5000
lsof -ti:5000

# Mátalο (reemplaza PID con el número que te dio el comando anterior)
kill -9 PID
```

### Error "port 5173 already in use"
```bash
# Encuentra el proceso usando el puerto 5173
lsof -ti:5173

# Mátalo
kill -9 PID
```

## 🔄 Para Detener la Aplicación

En cada terminal, presiona:
- **Control + C** (Cmd + C en Mac)

## 💾 Base de Datos

La primera vez que ejecutes el backend, creará automáticamente una base de datos SQLite en:
```
backend/laslira.db
```

Esta base de datos estará **vacía inicialmente**. Puedes:
1. Crear pedidos manualmente desde la interfaz
2. O importar datos desde los archivos Excel demo

## 🎨 Probar la Nueva Funcionalidad: Rutas Óptimas

1. Primero, crea algunos pedidos desde **"Pedidos"**
2. Asegúrate de seleccionar diferentes **comunas** para cada pedido
3. Ve a la sección **"Rutas"** en el menú
4. Prueba las 3 vistas:
   - **Hoy**: Ver entregas del día
   - **Esta Semana**: Planificación semanal
   - **Todos los Pendientes**: Vista completa

## 📝 Próximos Pasos

Una vez que la aplicación esté corriendo:
1. Explora las diferentes secciones
2. Crea algunos pedidos de prueba
3. Prueba el tablero Kanban arrastrando tarjetas
4. Experimenta con las rutas óptimas
5. Sube fotos a los productos

## 🆘 ¿Necesitas Ayuda?

Si algo no funciona, verifica:
1. ✅ Ambas terminales están corriendo (backend y frontend)
2. ✅ No hay errores en las terminales
3. ✅ El navegador está en `http://localhost:5173`
4. ✅ Las dependencias están instaladas correctamente

---

¡Disfruta usando Las-Lira! 🌸🌺🌻

