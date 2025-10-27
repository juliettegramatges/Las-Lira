# 🎨 Sistema de Análisis de Personalizaciones - Las Lira

## 📊 **RESUMEN DEL SISTEMA**

Este documento explica cómo el sistema permite crear, rastrear y analizar pedidos personalizados de forma detallada.

---

## 🏗️ **ESTRUCTURA DE LA BASE DE DATOS**

### **1. Tabla: `productos`**

Campos agregados para identificar productos personalizables:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `es_personalizacion` | BOOLEAN | `TRUE` si el producto es personalizable |
| `categoria_personalizacion` | VARCHAR(100) | Subcategoría: 'Ramo', 'Centro de Mesa', 'Bouquet', etc. |

**Ejemplo:**
```sql
-- Producto "Personalización" base
INSERT INTO productos (nombre, es_personalizacion, categoria_personalizacion) 
VALUES ('Personalización', TRUE, 'General');

-- Producto "Ramo Personalizado"
INSERT INTO productos (nombre, es_personalizacion, categoria_personalizacion) 
VALUES ('Ramo Personalizado', TRUE, 'Ramo');
```

---

### **2. Tabla: `pedidos`**

Campos agregados para rastrear detalles de personalizaciones:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `colores_solicitados` | TEXT | JSON con lista de colores: `['Rojo', 'Blanco', 'Verde']` |
| `tipo_personalizacion` | VARCHAR(100) | Tipo: 'Ramo', 'Centro de Mesa', 'Arreglo Especial', etc. |
| `notas_personalizacion` | TEXT | Notas específicas del cliente para la personalización |

**Ejemplo:**
```sql
-- Pedido personalizado con colores y tipo
INSERT INTO pedidos (
    producto_id, 
    cliente_nombre, 
    colores_solicitados, 
    tipo_personalizacion,
    notas_personalizacion
) VALUES (
    'PERS-001',
    'María García',
    '["Rojo", "Blanco", "Verde oscuro"]',
    'Ramo',
    'Cliente prefiere rosas rojas y evitar claveles'
);
```

---

### **3. Tabla: `pedidos_insumos`** (Ya existente)

Esta tabla **ya conecta cada pedido con sus insumos específicos**:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `pedido_id` | INTEGER | ID del pedido |
| `insumo_tipo` | ENUM | 'Flor' o 'Contenedor' |
| `insumo_id` | STRING(10) | ID del insumo usado |
| `cantidad` | INTEGER | Cantidad usada |
| `costo_unitario` | NUMERIC(10,2) | Costo por unidad |
| `costo_total` | NUMERIC(10,2) | Costo total |

**Esta tabla permite:**
- Saber exactamente qué flores y contenedores se usaron en cada personalización
- Calcular costos reales por pedido
- Analizar tendencias de uso de insumos

---

## 🔧 **INSTALACIÓN Y CONFIGURACIÓN**

### **Paso 1: Ejecutar la migración**

```bash
cd /Users/juliettegramatges/Las-Lira/backend
python3 scripts/mejorar_sistema_personalizaciones.py
```

Esto agregará:
- ✅ Campos `es_personalizacion` y `categoria_personalizacion` a `productos`
- ✅ Campos `colores_solicitados`, `tipo_personalizacion`, `notas_personalizacion` a `pedidos`
- ✅ Marcará el producto "Personalización" automáticamente

### **Paso 2: Reiniciar el backend**

```bash
cd /Users/juliettegramatges/Las-Lira/backend
python3 app.py
```

---

## 📊 **ENDPOINTS DE ANÁLISIS**

### **1. Análisis General de Personalizaciones**

**Endpoint:** `GET /api/analisis/personalizaciones`

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "resumen": {
      "total_pedidos": 150,
      "ingresos_totales": 4500000,
      "ticket_promedio": 30000
    },
    "por_tipo": [
      {
        "tipo": "Ramo",
        "cantidad": 80,
        "ingresos": 2400000
      },
      {
        "tipo": "Centro de Mesa",
        "cantidad": 40,
        "ingresos": 1600000
      }
    ],
    "flores_mas_usadas": [
      {
        "id": "FL001",
        "nombre": "Rosa Roja",
        "cantidad_total": 1200,
        "veces_usado": 85
      }
    ],
    "contenedores_mas_usados": [
      {
        "id": "CON001",
        "nombre": "Florero Cilíndrico",
        "veces_usado": 65
      }
    ],
    "colores_populares": [
      {"color": "Rojo", "cantidad": 95},
      {"color": "Blanco", "cantidad": 78},
      {"color": "Rosa", "cantidad": 65}
    ],
    "motivos_comunes": [
      {"motivo": "Cumpleaños", "cantidad": 45},
      {"motivo": "Aniversario", "cantidad": 30}
    ],
    "tendencia_temporal": [
      {
        "mes": "2025-01",
        "cantidad": 25,
        "ingresos": 750000
      }
    ]
  }
}
```

---

### **2. Detalle de Personalizaciones**

**Endpoint:** `GET /api/analisis/personalizaciones/detalle?page=1&limit=50`

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1234,
      "cliente_nombre": "María García",
      "arreglo_pedido": "Ramo personalizado rojo y blanco",
      "tipo_personalizacion": "Ramo",
      "colores_solicitados": "[\"Rojo\", \"Blanco\"]",
      "notas_personalizacion": "Cliente prefiere rosas",
      "precio_total": 35000,
      "insumos": [
        {
          "tipo": "Flor",
          "nombre": "Rosa Roja",
          "cantidad": 12,
          "costo_total": 6000
        },
        {
          "tipo": "Flor",
          "nombre": "Alstroemeria Blanca",
          "cantidad": 8,
          "costo_total": 3200
        },
        {
          "tipo": "Contenedor",
          "nombre": "Florero Cilíndrico",
          "cantidad": 1,
          "costo_total": 2500
        }
      ]
    }
  ],
  "total": 150,
  "page": 1,
  "total_pages": 3
}
```

---

## 📈 **CONSULTAS SQL ÚTILES**

### **1. Todas las personalizaciones**
```sql
SELECT p.*, prod.nombre as producto_nombre
FROM pedidos p
JOIN productos prod ON prod.id = p.producto_id
WHERE prod.es_personalizacion = TRUE
ORDER BY p.fecha_pedido DESC;
```

### **2. Personalizaciones por tipo**
```sql
SELECT 
    tipo_personalizacion,
    COUNT(*) as cantidad,
    SUM(precio_ramo + precio_envio) as ingresos_totales
FROM pedidos
WHERE producto_id IN (SELECT id FROM productos WHERE es_personalizacion = TRUE)
GROUP BY tipo_personalizacion
ORDER BY cantidad DESC;
```

### **3. Flores más usadas en personalizaciones**
```sql
SELECT 
    f.nombre,
    f.tipo,
    f.color,
    SUM(pi.cantidad) as cantidad_total,
    COUNT(DISTINCT pi.pedido_id) as veces_usado
FROM pedidos_insumos pi
JOIN flores f ON f.id = pi.insumo_id
JOIN pedidos p ON p.id = pi.pedido_id
JOIN productos prod ON prod.id = p.producto_id
WHERE prod.es_personalizacion = TRUE
  AND pi.insumo_tipo = 'Flor'
GROUP BY f.id
ORDER BY cantidad_total DESC
LIMIT 10;
```

### **4. Análisis de colores solicitados**
```sql
SELECT 
    colores_solicitados,
    COUNT(*) as cantidad
FROM pedidos
WHERE producto_id IN (SELECT id FROM productos WHERE es_personalizacion = TRUE)
  AND colores_solicitados IS NOT NULL
GROUP BY colores_solicitados
ORDER BY cantidad DESC;
```

### **5. Rentabilidad por personalización**
```sql
SELECT 
    p.id,
    p.cliente_nombre,
    p.precio_ramo + p.precio_envio as precio_total,
    SUM(pi.costo_total) as costo_insumos,
    (p.precio_ramo + p.precio_envio) - SUM(pi.costo_total) as margen
FROM pedidos p
LEFT JOIN pedidos_insumos pi ON pi.pedido_id = p.id
JOIN productos prod ON prod.id = p.producto_id
WHERE prod.es_personalizacion = TRUE
GROUP BY p.id
ORDER BY margen DESC;
```

---

## 🎯 **FLUJO DE TRABAJO**

### **Creando un Pedido Personalizado**

1. **Frontend:** Usuario selecciona "Personalización" como producto
2. **Frontend:** Usuario especifica:
   - Tipo de personalización: "Ramo", "Centro de Mesa", etc.
   - Colores deseados: ["Rojo", "Blanco", "Verde"]
   - Notas especiales
3. **Frontend:** Usuario selecciona insumos específicos (flores y contenedor)
4. **Backend:** Se crea el pedido con:
   - `producto_id` → ID del producto "Personalización"
   - `tipo_personalizacion` → "Ramo"
   - `colores_solicitados` → JSON con colores
   - `notas_personalizacion` → Notas del cliente
5. **Backend:** Se crean registros en `pedidos_insumos` con cada flor/contenedor usado

### **Analizando Personalizaciones**

1. **Dashboard:** Llamar a `/api/analisis/personalizaciones`
2. **Visualizar:**
   - Total de ingresos por personalizaciones
   - Tipos de personalización más populares
   - Flores y contenedores más usados
   - Colores más solicitados
   - Tendencia temporal (por mes)
3. **Detalle:** Llamar a `/api/analisis/personalizaciones/detalle` para ver cada pedido

---

## 💡 **VENTAJAS DEL SISTEMA**

✅ **Trazabilidad Completa:**
- Cada personalización tiene sus insumos específicos registrados
- Puedes saber exactamente qué flores y contenedores se usaron

✅ **Análisis de Rentabilidad:**
- Compara precio de venta vs costo real de insumos
- Identifica personalizaciones más rentables

✅ **Tendencias:**
- Identifica colores y flores más populares
- Ajusta inventario según demanda

✅ **Categorización:**
- Agrupa personalizaciones por tipo (Ramo, Centro de Mesa, etc.)
- Análisis separado por categoría

✅ **Flexibilidad:**
- Cada pedido puede tener insumos diferentes
- No hay recetas fijas para personalizaciones

---

## 🔄 **PRÓXIMOS PASOS**

1. **Ejecutar migración:**
   ```bash
   python3 backend/scripts/mejorar_sistema_personalizaciones.py
   ```

2. **Reiniciar backend:**
   ```bash
   python3 backend/app.py
   ```

3. **Crear página de análisis en el frontend:**
   - `/analisis/personalizaciones` → Dashboard con gráficos
   - Usar los endpoints `/api/analisis/personalizaciones` y `/api/analisis/personalizaciones/detalle`

4. **Actualizar formulario de pedidos:**
   - Agregar campos para `tipo_personalizacion` y `colores_solicitados`
   - Permitir selección de múltiples colores

5. **Reportes:**
   - Exportar a Excel análisis de personalizaciones
   - Gráficos de tendencias temporales

---

## 📞 **SOPORTE**

Si tienes dudas sobre el sistema, revisa:
- Este documento
- Código en `backend/routes/analisis_routes.py`
- Modelos en `backend/models/producto.py` y `backend/models/pedido.py`

---

✨ **¡Listo para analizar tus personalizaciones!** 🎨

