# 🔧 Solución: API Key para Backend

## Problema Actual

El error `API keys with referer restrictions cannot be used with this API` ocurre porque:

- **Frontend** necesita una API key con **restricciones de referente HTTP** (para Maps JavaScript API)
- **Backend** necesita una API key con **restricciones de IP** o **sin restricciones** (para Directions API)

**No puedes usar la misma API key con restricciones de referente para el backend.**

## ✅ Solución: Crear Segunda API Key

### Paso 1: Crear Nueva API Key para Backend

1. Ve a [Google Cloud Console → Credenciales](https://console.cloud.google.com/apis/credentials)
2. Haz clic en **"+ CREAR CREDENCIALES"** → **"Clave de API"**
3. Se creará una nueva API Key, cópiala

### Paso 2: Configurar Restricciones

1. Haz clic en la nueva API Key para editarla

2. **Restricciones de aplicación:**
   - Selecciona: **"Restricciones de IP"** (o **"Ninguna"** para desarrollo local)
   - Si eliges "Restricciones de IP", agrega:
     - `127.0.0.1` (localhost)
     - Tu IP pública (puedes verla en https://whatismyipaddress.com/)

3. **Restricciones de API:**
   - Selecciona: **"Restringir clave"**
   - Habilita SOLO estas APIs:
     - ✅ **Directions API** (obligatorio)
     - ✅ **Geocoding API** (para geocodificar direcciones)

4. Haz clic en **"Guardar"**

### Paso 3: Habilitar APIs

Si no están habilitadas, ve a [API Library](https://console.cloud.google.com/apis/library) y habilita:
- **Directions API**
- **Geocoding API**

### Paso 4: Actualizar Backend

1. Abre `backend/.env`
2. Reemplaza la API key actual con la nueva:
   ```env
   GOOGLE_MAPS_API_KEY=tu_nueva_api_key_aqui
   ```
3. Reinicia el backend

### Paso 5: Verificar

Intenta optimizar una ruta. Deberías ver en los logs del backend:
```
✅ Ruta optimizada con Google Maps Directions API
```

En lugar de:
```
⚠️ Usando optimización simple (Google API error: ...)
```

---

## 📋 Resumen de Configuración

| Componente | API Key | Restricción | Variable de Entorno |
|------------|---------|-------------|---------------------|
| **Frontend** | API Key 1 | Referentes HTTP: `http://localhost:3001/*` | `VITE_GOOGLE_MAPS_API_KEY` |
| **Backend** | API Key 2 | Restricciones de IP (o Ninguna) | `GOOGLE_MAPS_API_KEY` |

---

## ⚠️ Nota Importante

- **NO uses la misma API key** para frontend y backend si tiene restricciones de referente
- El backend **NO puede usar** API keys con restricciones de referente HTTP
- Para desarrollo local, puedes usar **"Ninguna"** en restricciones de aplicación para el backend

---

## 🔍 Verificar que Funciona

Después de configurar, los logs del backend mostrarán:
- ✅ `Ruta optimizada con Google Maps Directions API` (si funciona)
- ⚠️ `Usando optimización simple` (si aún hay problemas)

