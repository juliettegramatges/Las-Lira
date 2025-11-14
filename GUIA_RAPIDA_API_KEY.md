# 🚀 Guía Rápida: Configurar API Key de Google Maps

## Problema
```
❌ Error: API keys with referer restrictions cannot be used with this API
```

## ✅ Solución en 5 Pasos (2 minutos)

### Paso 1: Ir a Google Cloud Console
🔗 https://console.cloud.google.com/apis/credentials

### Paso 2: Editar tu API Key
1. Encuentra tu API Key actual (la que usas en `VITE_GOOGLE_MAPS_API_KEY`)
2. Haz clic en el ícono de lápiz ✏️ para editar

### Paso 3: Cambiar Restricciones de Aplicación
**Opción A - Más Fácil (Desarrollo):**
- Selecciona: **"Ninguna"**

**Opción B - Más Segura (Si insistes en restricciones):**
- Selecciona: **"Direcciones IP"**
- Agrega estas IPs:
  ```
  127.0.0.1
  192.168.0.0/16
  ::1
  ```

### Paso 4: Configurar Restricciones de API
1. Selecciona: **"Restringir clave"**
2. Marca estas APIs:
   - ✅ **Maps JavaScript API** (para el mapa en el navegador)
   - ✅ **Places API** (para buscar direcciones)
   - ✅ **Directions API** ⬅️ **¡IMPORTANTE! Esto es lo que necesita el backend**
   - ✅ **Geocoding API** (opcional, para convertir direcciones a coordenadas)

### Paso 5: Guardar y Esperar
1. Haz clic en **"Guardar"**
2. ⏱️ Espera 1-2 minutos (los cambios tardan en propagarse)
3. Recarga tu aplicación y prueba la optimización de ruta

---

## 🔍 Verificar que Funciona

### En el Backend (Terminal)
Deberías ver:
```bash
✅ Ruta optimizada: Ruta optimizada con Google Maps Directions API
```

En lugar de:
```bash
⚠️ Ruta optimizada: Usando optimización simple
```

### En el Frontend
- El mapa debe mostrar la ruta con curvas reales de calles
- El botón "Abrir Navegación en Google Maps" debe funcionar

---

## 💡 Recomendaciones

### Para Desarrollo (Local):
✅ **Usa restricción "Ninguna"** - Es más fácil y no tienes riesgos de seguridad en localhost

### Para Producción:
✅ **Crea DOS API Keys separadas:**

| Componente | Restricción | Variable de Entorno | APIs Habilitadas |
|------------|-------------|---------------------|------------------|
| Frontend | Referente HTTP | `VITE_GOOGLE_MAPS_API_KEY` | Maps JS, Places |
| Backend | IP del servidor | `GOOGLE_MAPS_API_KEY` | Directions |

---

## 🆘 Si Sigue Sin Funcionar

### 1. Verificar que la API está habilitada:
🔗 https://console.cloud.google.com/apis/library/directions-backend.googleapis.com
- Haz clic en **"Habilitar"** si no lo está

### 2. Verificar límites y cuotas:
🔗 https://console.cloud.google.com/apis/api/directions-backend.googleapis.com/quotas
- Verifica que no hayas excedido el límite gratuito

### 3. Verificar método de pago:
🔗 https://console.cloud.google.com/billing
- Google requiere una tarjeta asociada, aunque tiene $200 USD gratis al mes

### 4. Verificar variable de entorno:
```bash
# En backend/.env
GOOGLE_MAPS_API_KEY=tu_api_key_aqui
```

---

## 💰 Costos

Google Maps ofrece **$200 USD en créditos gratis cada mes**, que equivale a:
- **40,000 solicitudes** a Directions API ($5 por 1,000)
- Si optimizas 20 rutas al día = 600 solicitudes/mes = **$3 USD** (cubierto por el crédito gratuito)

**No pagarás nada** a menos que superes los $200 USD/mes.

---

## 🎯 Resumen Ultra Rápido

1. Ve a: https://console.cloud.google.com/apis/credentials
2. Edita tu API Key
3. Cambiar restricción a **"Ninguna"**
4. Habilitar **"Directions API"**
5. Guardar y esperar 2 minutos
6. ✅ Listo!
