# 🗺️ Sistema de Rutas Optimizadas - Las Lira

## 📋 Resumen

Se ha implementado un **sistema completo de selección de direcciones con Google Maps y optimización de rutas** para el sistema de gestión de pedidos de Las Lira.

---

## ✨ Características Implementadas

### 1. 📍 Selección de Dirección con Mapa Interactivo

**Ubicación:** Formulario de edición de pedidos

**Funcionalidades:**
- **Autocompletado inteligente** de direcciones en Chile
- **Mapa interactivo** con Google Maps
- **Marcador arrastrable** para ajustar ubicación exacta
- **Detección automática de comuna**
- **Geocodificación:** Convierte direcciones a coordenadas GPS y viceversa
- **Búsqueda en el mapa** para localizar direcciones

**Componente:** `frontend/src/components/common/DireccionConMapa.jsx`

---

### 2. 🚚 Optimización de Rutas de Entrega

**Ubicación:** Página de Rutas (`/rutas`)

**Funcionalidades:**
- **Selección de pedidos** a incluir en la ruta
- **Configuración de hora de inicio** personalizable (default: 09:00)
- **Punto de inicio predeterminado:** Gran Vía 8113, Vitacura
- **Optimización automática** usando:
  - Google Maps Directions API (cuando hay API Key)
  - Algoritmo de vecino más cercano (fallback)
- **Cálculo de:**
  - Distancia total (km)
  - Tiempo estimado (minutos)
  - Distancia y tiempo entre cada parada
- **Visualización en mapa** con:
  - Marcador verde para punto de inicio (🏠)
  - Marcadores numerados para cada parada
  - Marcadores rojos para pedidos urgentes
  - Línea de ruta dibujada en el mapa
  - InfoWindows con detalles al hacer clic
- **Lista secuencial de entregas** con toda la información

**Componente:** `frontend/src/components/Rutas/RutaOptimizada.jsx`

---

## 🗄️ Cambios en la Base de Datos

### Modelo Pedido - Nuevas Columnas

```python
latitud = db.Column(db.Float)      # Latitud GPS
longitud = db.Column(db.Float)     # Longitud GPS
```

**Migración ejecutada:** ✅
```bash
python3 backend/scripts/agregar_coordenadas_pedidos.py
```

---

## 📁 Archivos Creados/Modificados

### Backend

**Nuevos archivos:**
- ✅ `backend/config/rutas_config.py` - Configuración de punto de inicio y parámetros
- ✅ `backend/services/rutas_service.py` - Servicio de optimización de rutas
- ✅ `backend/scripts/agregar_coordenadas_pedidos.py` - Migración de BD
- ✅ `backend/.env` - Variables de entorno (API Key)

**Modificados:**
- ✅ `backend/models/pedido.py` - Agregadas columnas `latitud` y `longitud`
- ✅ `backend/routes/pedidos_routes.py` - Endpoint `/rutas/optimizar`

### Frontend

**Nuevos archivos:**
- ✅ `frontend/src/components/common/DireccionConMapa.jsx` - Selector de dirección
- ✅ `frontend/src/components/Rutas/RutaOptimizada.jsx` - Visualización de ruta
- ✅ `frontend/.env` - Variables de entorno (API Key)

**Modificados:**
- ✅ `frontend/src/pages/RutasPage.jsx` - Integración de optimización
- ✅ `frontend/src/pages/PedidosPage.jsx` - Integración de selector de dirección

### Documentación

- ✅ `INSTRUCCIONES_GOOGLE_MAPS.md` - Guía completa para obtener API Key
- ✅ `SISTEMA_DE_RUTAS.md` - Este archivo
- ✅ `.env.example` - Ejemplos de configuración

---

## 🚀 Cómo Usar

### Paso 1: Obtener Google Maps API Key

Sigue las instrucciones detalladas en: **`INSTRUCCIONES_GOOGLE_MAPS.md`**

### Paso 2: Configurar API Keys

1. **Backend:** Edita `backend/.env`
   ```env
   GOOGLE_MAPS_API_KEY=TU_API_KEY_AQUI
   ```

2. **Frontend:** Edita `frontend/.env`
   ```env
   VITE_GOOGLE_MAPS_API_KEY=TU_API_KEY_AQUI
   ```

### Paso 3: Reiniciar Servidores

```bash
# Backend (terminal 1)
cd backend
python3 app.py

# Frontend (terminal 2)
cd frontend
npm run dev
```

---

## 📖 Uso del Sistema

### Agregar/Editar Dirección en Pedidos

1. Ve a **Pedidos** → Edita un pedido o crea uno nuevo
2. En la sección **"Dirección de Entrega"**:
   - Escribe una dirección en el campo de búsqueda
   - Selecciona de las sugerencias autocompletadas
   - **O** haz clic en "Buscar en el mapa"
   - **O** arrastra el marcador rojo en el mapa
3. La comuna se detecta automáticamente
4. Las coordenadas GPS se guardan en segundo plano

### Optimizar Ruta de Entregas

1. Ve a **Rutas**
2. Selecciona la fecha de entrega
3. **Selecciona los pedidos** que quieres incluir en la ruta (checkbox)
4. Configura la **hora de inicio** (ej: 09:00)
5. Haz clic en **"Optimizar Ruta (X)"**
6. Aparecerá la pestaña **"Ruta Optimizada"** con:
   - Mapa interactivo con la ruta dibujada
   - Resumen: distancia total, tiempo, paradas
   - Lista secuencial de entregas ordenadas
   - Detalles de cada parada

### Marcar Pedidos como Despachados

- Desde la vista de "Ruta Optimizada" o "Rutas por Comuna"
- Selecciona los pedidos
- Clic en **"Marcar como Despachados"**

---

## 🧩 Arquitectura Técnica

### Flujo de Datos - Selección de Dirección

```
Usuario escribe dirección
    ↓
Google Places Autocomplete API
    ↓
Usuario selecciona sugerencia
    ↓
Geocoding API obtiene coordenadas
    ↓
Se guarda: dirección + comuna + latitud + longitud
    ↓
Base de datos actualizada
```

### Flujo de Datos - Optimización de Rutas

```
Usuario selecciona pedidos + hora inicio
    ↓
Backend: /api/pedidos/rutas/optimizar
    ↓
RutasService.optimizar_ruta_google()
    ↓
┌─────────────────────────┐
│ ¿Hay Google API Key?    │
└─────────────────────────┘
        ↓ Sí                    ↓ No
Google Directions API        Algoritmo Simple
(waypoint optimization)      (vecino más cercano)
        ↓                         ↓
Ruta optimizada con       Ruta usando distancias
distancias reales         en línea recta (Haversine)
        ↓                         ↓
        └─────────┬───────────────┘
                  ↓
    Frontend: RutaOptimizada.jsx
                  ↓
    Visualización en mapa + lista
```

---

## 🔧 Configuración Técnica

### Punto de Inicio (Tienda)

Ubicado en: `backend/config/rutas_config.py`

```python
PUNTO_INICIO = {
    'nombre': 'Las Lira - Tienda',
    'direccion': 'Gran Vía 8113, Vitacura, Región Metropolitana, Chile',
    'latitud': -33.4006,
    'longitud': -70.5721,
    'comuna': 'Vitacura'
}
```

**Para cambiar:** Edita este archivo y reinicia el backend.

### APIs de Google Maps Utilizadas

1. **Maps JavaScript API** - Renderizado del mapa
2. **Places API** - Autocompletado de direcciones
3. **Geocoding API** - Conversión dirección ↔ coordenadas
4. **Directions API** - Optimización de rutas y cálculo de distancias/tiempos

---

## 💰 Costos Estimados

**Crédito gratis:** $200 USD/mes

**Uso estimado para Las Lira:**
- 50 pedidos/día con selector de mapa = ~$5/mes
- 10 optimizaciones de ruta/día = ~$2/mes
- **Total:** ~$7-10 USD/mes (100% cubierto por crédito gratis)

Ver más detalles en: `INSTRUCCIONES_GOOGLE_MAPS.md`

---

## 🐛 Solución de Problemas

### El mapa no carga

**Síntoma:** Aparece pantalla gris o "For development purposes only"

**Soluciones:**
1. Verifica que la API Key esté en `frontend/.env` y `backend/.env`
2. Reinicia el servidor frontend (`Ctrl+C` y `npm run dev`)
3. Revisa que hayas habilitado las 4 APIs en Google Cloud Console
4. Verifica que la cuenta de facturación esté activa

### La optimización no usa Google (usa "simple")

**Síntoma:** El mensaje dice "algoritmo simple" en lugar de "Google Directions API"

**Soluciones:**
1. Verifica que `GOOGLE_MAPS_API_KEY` esté en `backend/.env`
2. Reinicia el servidor backend
3. Verifica que "Directions API" esté habilitada en Google Cloud Console

### Error: "REQUEST_DENIED"

**Causa:** API Key inválida o no autorizada

**Soluciones:**
1. Verifica que copiaste correctamente la API Key (sin espacios)
2. Ve a Google Cloud Console → Credenciales y verifica que la key esté activa
3. Asegúrate de haber habilitado todas las APIs necesarias

---

## 🔐 Seguridad

⚠️ **IMPORTANTE:**

- Los archivos `.env` **NO se suben a GitHub** (están en `.gitignore`)
- **NUNCA** compartas tu API Key públicamente
- Configura **restricciones de API** en Google Cloud Console
- Configura **alertas de presupuesto** para controlar costos

---

## 📚 Recursos

- [Documentación Google Maps Platform](https://developers.google.com/maps/documentation)
- [Precios Google Maps](https://mapsplatform.google.com/pricing/)
- [Google Cloud Console](https://console.cloud.google.com/)

---

## ✅ Checklist de Implementación

- [x] Modelo de BD actualizado con coordenadas
- [x] Migración de BD ejecutada
- [x] Componente DireccionConMapa creado
- [x] Integrado en formulario de pedidos
- [x] Servicio de optimización de rutas (backend)
- [x] Endpoint API para optimización
- [x] Componente RutaOptimizada con mapa
- [x] Integrado en página de Rutas
- [x] Configuración de punto de inicio
- [x] Archivos .env creados
- [x] Documentación completa
- [x] Fallback sin API Key (algoritmo simple)

---

## 🎉 ¡Todo Listo!

El sistema está completamente implementado y listo para usar. Solo falta:

1. ✅ Obtener tu Google Maps API Key (sigue `INSTRUCCIONES_GOOGLE_MAPS.md`)
2. ✅ Configurar las API Keys en los archivos `.env`
3. ✅ Reiniciar los servidores
4. ✅ ¡Empezar a usar el sistema!

---

**Desarrollado con ❤️ para Las Lira Florería**
