# 🗺️ Instrucciones para Obtener Google Maps API Key

Este documento te guiará paso a paso para obtener tu API Key de Google Maps Platform, necesaria para el sistema de selección de direcciones y optimización de rutas.

## 📋 Requisitos Previos

- Una cuenta de Google (Gmail)
- Una tarjeta de crédito o débito (para verificación, Google ofrece $200 USD de crédito gratis mensualmente)

---

## 🚀 Paso 1: Crear un Proyecto en Google Cloud Console

1. Ve a la consola de Google Cloud:
   👉 https://console.cloud.google.com/

2. **Inicia sesión** con tu cuenta de Google

3. **Crear un nuevo proyecto:**
   - Haz clic en el selector de proyectos (parte superior)
   - Clic en "NUEVO PROYECTO"
   - Nombre del proyecto: **"Las Lira - Sistema de Rutas"** (o el que prefieras)
   - Clic en **"CREAR"**

4. **Espera** unos segundos mientras se crea el proyecto

---

## 💳 Paso 2: Configurar Facturación (IMPORTANTE)

Google Maps requiere una cuenta de facturación activa, pero ofrece **$200 USD de crédito gratis cada mes**.

1. En el menú lateral, ve a:
   **Facturación** → **Vincular una cuenta de facturación**

2. Sigue los pasos para crear una cuenta de facturación:
   - Selecciona tu país: **Chile**
   - Acepta los términos y condiciones
   - Ingresa los datos de tu tarjeta de crédito/débito

3. **NOTA IMPORTANTE:** Con el uso normal del sistema (direcciones y rutas), NO deberías superar los $200 USD mensuales gratuitos. Google NO te cobrará automáticamente si superas el límite sin tu autorización.

---

## 🔑 Paso 3: Habilitar las APIs Necesarias

Necesitas habilitar 3 APIs:

### 3.1 Maps JavaScript API

1. En el menú lateral, ve a: **APIs y servicios** → **Biblioteca**

2. Busca: **"Maps JavaScript API"**

3. Haz clic en el resultado y luego en **"HABILITAR"**

### 3.2 Places API

1. En la Biblioteca de APIs, busca: **"Places API"**

2. Haz clic y selecciona **"HABILITAR"**

### 3.3 Directions API

1. En la Biblioteca de APIs, busca: **"Directions API"**

2. Haz clic y selecciona **"HABILITAR"**

### 3.4 Geocoding API

1. En la Biblioteca de APIs, busca: **"Geocoding API"**

2. Haz clic y selecciona **"HABILITAR"**

---

## 🔐 Paso 4: Crear la API Key

1. En el menú lateral, ve a:
   **APIs y servicios** → **Credenciales**

2. Haz clic en **"+ CREAR CREDENCIALES"** (parte superior)

3. Selecciona **"Clave de API"**

4. ¡Se creará tu API Key! Cópiala, la verás así:
   ```
   AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

5. **IMPORTANTE:** Haz clic en **"RESTRINGIR CLAVE"** (recomendado para seguridad)

---

## 🛡️ Paso 5: Restringir la API Key (Recomendado)

### 5.1 Restricciones de API

1. En la sección **"Restricciones de la API"**, selecciona:
   ☑️ **"Restringir clave"**

2. Marca las siguientes APIs:
   - ☑️ Maps JavaScript API
   - ☑️ Places API
   - ☑️ Directions API
   - ☑️ Geocoding API

3. Haz clic en **"GUARDAR"**

### 5.2 Restricciones de Aplicación (Opcional - Para Producción)

Si vas a publicar el sistema en internet, puedes restringir por dominio:

1. En **"Restricciones de la aplicación"**, selecciona:
   - **"Referentes HTTP (sitios web)"**

2. Agrega tus dominios permitidos:
   ```
   localhost/*
   http://localhost:*/*
   https://tudominio.com/*
   ```

3. Haz clic en **"GUARDAR"**

---

## 📝 Paso 6: Configurar la API Key en el Proyecto

### 6.1 Backend

1. Abre el archivo: `/backend/.env`

2. Pega tu API Key:
   ```env
   GOOGLE_MAPS_API_KEY=AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

### 6.2 Frontend

1. Abre el archivo: `/frontend/.env`

2. Pega tu API Key:
   ```env
   VITE_GOOGLE_MAPS_API_KEY=AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

3. **IMPORTANTE:** Después de modificar el archivo `.env` del frontend, reinicia el servidor de desarrollo:
   ```bash
   # Detén el servidor (Ctrl+C)
   # Luego reinicia:
   npm run dev
   ```

---

## ✅ Paso 7: Verificar que Funciona

1. **Reinicia el backend** (si estaba corriendo):
   ```bash
   cd backend
   python3 app.py
   ```

2. **Reinicia el frontend** (si estaba corriendo):
   ```bash
   cd frontend
   npm run dev
   ```

3. **Prueba el sistema:**
   - Ve a la página de **Pedidos**
   - Haz clic en **"+ Nuevo Pedido"** o edita un pedido existente
   - En la sección de **"Dirección de Entrega"**, deberías ver:
     - ✅ Un campo de búsqueda con autocompletado
     - ✅ Un mapa interactivo
     - ✅ Un marcador que puedes arrastrar

4. **Prueba las rutas optimizadas:**
   - Ve a la página de **Rutas**
   - Selecciona varios pedidos
   - Haz clic en **"Optimizar Ruta"**
   - Deberías ver la ruta optimizada en el mapa

---

## 💰 Monitoreo de Uso y Costos

### Ver tu uso actual:

1. En Google Cloud Console, ve a:
   **APIs y servicios** → **Panel de control**

2. Podrás ver:
   - Solicitudes por día
   - Cuota utilizada
   - Costos estimados

### Configurar alertas de presupuesto:

1. Ve a **Facturación** → **Presupuestos y alertas**

2. Crea un presupuesto:
   - Monto: $50 USD (como ejemplo)
   - Alertas: Al 50%, 90% y 100%

---

## 📊 Costos Estimados (Referencia 2025)

Google ofrece **$200 USD de crédito gratis mensualmente**. Los costos son aproximadamente:

| API | Costo por 1,000 solicitudes | Incluido en $200 gratis |
|-----|----------------------------|------------------------|
| **Maps JavaScript API** | $7 USD | ~28,500 cargas de mapa |
| **Places API (Autocomplete)** | $2.83 USD por sesión | ~70,000 búsquedas |
| **Directions API** | $5 USD | ~40,000 rutas |
| **Geocoding API** | $5 USD | ~40,000 geocodificaciones |

**Para tu negocio:**
- Si creas **50 pedidos al día** = ~1,500 pedidos/mes
- Optimizas rutas **10 veces al día** = ~300 rutas/mes
- **Costo estimado mensual: ~$10-15 USD** (bajo del límite de $200 USD gratis)

---

## 🚨 Solución de Problemas

### Error: "RefererNotAllowedMapError"
**Causa:** La API Key está restringida por dominio
**Solución:** Agrega `localhost/*` y `http://localhost:*/*` en las restricciones de referentes

### Error: "This API project is not authorized to use this API"
**Causa:** No has habilitado la API necesaria
**Solución:** Ve a "Biblioteca de APIs" y habilita todas las APIs mencionadas en el Paso 3

### El mapa no carga / muestra "For development purposes only"
**Causa:** La cuenta de facturación no está configurada
**Solución:** Configura la facturación en el Paso 2

### Error: "REQUEST_DENIED"
**Causa:** La API Key no es válida o está mal copiada
**Solución:** Verifica que copiaste correctamente la API Key en los archivos `.env`

### El autocompletado no funciona
**Causa:** Places API no está habilitada
**Solución:** Habilita "Places API" en la biblioteca de APIs

### La ruta optimizada no se genera
**Causa:** Directions API no está habilitada
**Solución:** Habilita "Directions API" en la biblioteca de APIs

---

## 🔒 Seguridad - Mejores Prácticas

1. **NUNCA** compartas tu API Key públicamente
2. **NUNCA** subas archivos `.env` a GitHub (ya están en `.gitignore`)
3. **SIEMPRE** usa restricciones de API
4. **Configura alertas** de presupuesto
5. **Revisa el uso** mensualmente
6. **Rota la API Key** si crees que fue comprometida:
   - Ve a Credenciales → tu API Key → Regenerar clave

---

## 📞 Soporte

- **Documentación oficial:** https://developers.google.com/maps/documentation
- **Precios:** https://mapsplatform.google.com/pricing/
- **Soporte de Google:** https://support.google.com/googleapi/

---

## ✨ ¡Listo!

Ahora tu sistema de pedidos de Las Lira cuenta con:
- ✅ Selección de dirección con mapa interactivo
- ✅ Autocompletado de direcciones en Chile
- ✅ Detección automática de comunas
- ✅ Optimización de rutas de entrega
- ✅ Cálculo de distancias y tiempos
- ✅ Visualización de rutas en mapa

¡Disfruta de tu nuevo sistema de rutas optimizadas! 🚚🌸
