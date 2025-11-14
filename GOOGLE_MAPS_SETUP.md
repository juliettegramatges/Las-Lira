# Configuración de Google Maps API

## Problema Actual

El error `API keys with referer restrictions cannot be used with this API` ocurre porque estás usando una API Key configurada con **restricciones de referente HTTP** (dominio web) para llamadas desde el backend.

Google Maps tiene dos tipos de APIs:
- **APIs del lado del cliente** (Maps JavaScript API): Se usan en el navegador
- **APIs del lado del servidor** (Directions API): Se usan desde el backend

## Solución: Dos API Keys Diferentes

### 1. API Key para el Frontend (Ya la tienes)
- **Uso**: Maps JavaScript API, Places API
- **Restricción**: Restricciones de referente HTTP
- **Dominios permitidos**:
  - `http://localhost:*`
  - `http://127.0.0.1:*`
  - Tu dominio de producción (ej: `https://laslira.cl/*`)
- **Variable de entorno**: `VITE_GOOGLE_MAPS_API_KEY` (en `.env` del frontend)

### 2. API Key para el Backend (Necesitas crear esta)
- **Uso**: Directions API (optimización de rutas)
- **Restricción**: Restricciones de IP (o sin restricciones para desarrollo)
- **Variable de entorno**: `GOOGLE_MAPS_API_KEY` (en `.env` del backend)

## Pasos para Configurar la API Key del Backend

### Paso 1: Crear nueva API Key
1. Ve a [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Selecciona tu proyecto
3. Haz clic en **"Crear credenciales"** → **"Clave de API"**

### Paso 2: Configurar Restricciones
1. Haz clic en la nueva API Key para editarla
2. En **"Restricciones de clave"**:
   - Selecciona **"Restricciones de IP"**
   - Para desarrollo: Deja sin restricciones o agrega tu IP
   - Para producción: Agrega la IP de tu servidor
3. En **"Restricciones de API"**:
   - Selecciona **"Restringir clave"**
   - Habilita solo: **Directions API**

### Paso 3: Habilitar la API
1. Ve a [API Library](https://console.cloud.google.com/apis/library)
2. Busca **"Directions API"**
3. Haz clic en **"Habilitar"**

### Paso 4: Agregar al Backend
Crea o edita el archivo `backend/.env`:

```bash
GOOGLE_MAPS_API_KEY=tu_api_key_de_backend_aqui
```

⚠️ **Importante**: No compartas esta API Key en repositorios públicos. Asegúrate de que `.env` esté en `.gitignore`.

## Alternativa: Usar Solo el Algoritmo Simple

Si no quieres pagar por la API de Directions, el sistema funciona perfectamente con el **algoritmo simple** que ya está implementado:

### Ventajas del Algoritmo Simple:
✅ **Gratuito** - No usa APIs de pago
✅ **Funciona sin internet** - Usa cálculos GPS locales
✅ **Genera link de navegación** - El conductor puede abrir Google Maps
✅ **Optimización vecino más cercano** - Buen resultado para la mayoría de casos
✅ **Velocidad ajustada** - 40 km/h promedio para ciudad

### Diferencias con Google Directions API:
- ❌ No considera tráfico en tiempo real
- ❌ No considera calles de un solo sentido
- ❌ Distancias en línea recta (Haversine) vs rutas reales
- ✅ Pero el **link de navegación funciona igual** - Google Maps calcula la ruta real cuando el conductor la abre

### Cuándo usar cada uno:
- **Algoritmo Simple**: Desarrollo, pruebas, o si tienes presupuesto limitado
- **Google Directions API**: Producción con muchas entregas diarias donde la optimización es crítica

## Costos de Google Directions API

- Precio: $5 USD por cada 1,000 solicitudes
- Cada optimización de ruta = 1 solicitud
- Ejemplo: 20 rutas optimizadas al día = ~$3 USD/mes

## Verificar que Funciona

### Sin API Key (Algoritmo Simple):
```bash
# Backend debe mostrar:
⚠️  No se encontró API Key de Google, usando optimización simple
✅ Ruta optimizada: Usando optimización simple
```

### Con API Key (Google Directions):
```bash
# Backend debe mostrar:
✅ Ruta optimizada: Ruta optimizada con Google Maps Directions API
```

## Resumen

| Componente | API Key | Restricción | APIs Habilitadas |
|------------|---------|-------------|-------------------|
| Frontend | `VITE_GOOGLE_MAPS_API_KEY` | Referente HTTP | Maps JavaScript, Places |
| Backend | `GOOGLE_MAPS_API_KEY` | IP o sin restricción | Directions |

**Importante**: Ambas API Keys pueden ser de la misma cuenta de Google Cloud, pero deben tener restricciones diferentes.

---

## Estado Actual del Sistema

✅ El sistema **funciona perfectamente** con el algoritmo simple
✅ El **link de navegación** se genera correctamente
✅ El conductor puede **abrir Google Maps** y seguir la ruta
✅ La **visualización en el mapa** funciona

El único cambio al agregar la API Key de backend es que las rutas serán más precisas considerando calles y tráfico real.
