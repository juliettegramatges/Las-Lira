# 🎨 Propuesta: Sistema de Colores y Flores por Arreglo

## 📋 Problema Actual

- Los productos tienen colores y flores como texto simple
- No hay forma de seleccionar flores específicas al crear un pedido
- No se puede ajustar cantidades por color
- No hay flexibilidad para cambiar flores según disponibilidad

## ✨ Solución Propuesta

### 1. Nueva Estructura de Datos

#### Tabla: `producto_colores`
Define los colores específicos de cada producto con cantidades sugeridas.

```sql
CREATE TABLE producto_colores (
    id INTEGER PRIMARY KEY,
    producto_id VARCHAR(10) REFERENCES productos(id),
    nombre_color VARCHAR(50) NOT NULL,  -- "Rojo", "Blanco", "Verde oscuro"
    cantidad_flores_sugerida INTEGER,    -- 12, 5, 3, etc.
    orden INTEGER,                       -- Para ordenar visualmente
    notas TEXT
);
```

#### Tabla: `producto_color_flores`
Define qué flores están disponibles para cada color de cada producto.

```sql
CREATE TABLE producto_color_flores (
    id INTEGER PRIMARY KEY,
    producto_color_id INTEGER REFERENCES producto_colores(id),
    flor_id VARCHAR(10) REFERENCES flores(id),
    es_predeterminada BOOLEAN DEFAULT FALSE,  -- La que se usa por defecto
    notas TEXT
);
```

#### Tabla: `pedido_flores_seleccionadas`
Guarda las flores específicas seleccionadas en cada pedido.

```sql
CREATE TABLE pedido_flores_seleccionadas (
    id INTEGER PRIMARY KEY,
    pedido_id VARCHAR(20) REFERENCES pedidos(id),
    producto_color_id INTEGER REFERENCES producto_colores(id),
    flor_id VARCHAR(10) REFERENCES flores(id),
    cantidad INTEGER NOT NULL,
    color_nombre VARCHAR(50),  -- Para referencia
    costo_unitario DECIMAL(10,2),
    costo_total DECIMAL(10,2)
);
```

### 2. Ejemplo Completo: "Pasión Roja"

#### Paso 1: Definir Producto
```python
Producto: PR001 - "Pasión Roja"
  Tipo: Con Florero
  Precio: $35,000
```

#### Paso 2: Definir Colores
```python
producto_colores:
  - id: 1, producto_id: PR001, color: "Rojo", cantidad: 12, orden: 1
  - id: 2, producto_id: PR001, color: "Verde oscuro", cantidad: 5, orden: 2
```

#### Paso 3: Definir Flores Disponibles por Color
```python
producto_color_flores:
  Color "Rojo" (id: 1):
    - Rosa roja (FL001) [predeterminada]
    - Clavel rojo (FL008)
    - Gerbera roja (FL015)
  
  Color "Verde oscuro" (id: 2):
    - Eucalipto (FL019) [predeterminada]
    - Ruscus (FL021)
```

#### Paso 4: Al Crear Pedido
```
Cliente pide: "Pasión Roja" para el 25/10/2025

Interfaz muestra:
┌─────────────────────────────────────────┐
│ Arreglo: Pasión Roja                    │
├─────────────────────────────────────────┤
│ Color: Rojo (sugerido: 12 flores)      │
│ Flor: [Rosa roja ▼]  Cantidad: [12]    │
│   Opciones: Rosa roja, Clavel rojo,    │
│             Gerbera roja                │
├─────────────────────────────────────────┤
│ Color: Verde oscuro (sugerido: 5)      │
│ Flor: [Eucalipto ▼]  Cantidad: [5]     │
│   Opciones: Eucalipto, Ruscus          │
├─────────────────────────────────────────┤
│ Contenedor: Florero Vidrio Cilíndrico  │
│ [Florero vidrio mediano ▼] Cant: [1]   │
└─────────────────────────────────────────┘
```

### 3. Flujo Completo

#### A. Configuración Inicial (una vez)
1. Crear producto "Pasión Roja"
2. Definir sus colores: Rojo (12 flores), Verde (5 flores)
3. Asociar flores disponibles:
   - Rojo → Rosa roja, Clavel rojo, Gerbera roja
   - Verde → Eucalipto, Ruscus

#### B. Al Crear Pedido
1. Cliente selecciona "Pasión Roja"
2. Sistema muestra colores y flores disponibles
3. Florista selecciona:
   - Color Rojo: **Clavel rojo** x 10 (ajustó de 12 a 10)
   - Color Verde: **Eucalipto** x 5
   - Contenedor: Florero mediano x 1
4. Sistema verifica stock disponible
5. Si todo OK, crea el pedido
6. Guarda en `pedido_flores_seleccionadas`:
   ```
   - pedido: PED010, color: "Rojo", flor: FL008 (Clavel rojo), cant: 10
   - pedido: PED010, color: "Verde", flor: FL019 (Eucalipto), cant: 5
   ```
7. Al confirmar pedido, descuenta stock:
   - FL008 (Clavel rojo): -10 unidades
   - FL019 (Eucalipto): -5 unidades
   - CO002 (Florero mediano): -1 unidad

### 4. Ventajas del Sistema

✅ **Flexibilidad**: Cambiar flores según disponibilidad
✅ **Precisión**: Saber exactamente qué flor se usó en cada pedido
✅ **Trazabilidad**: Historial completo de insumos por pedido
✅ **Costos reales**: Calcular costo real vs. costo estimado
✅ **Gestión de stock**: Descuento preciso de inventario
✅ **Temporadas**: Fácil cambiar flores disponibles por temporada

### 5. Interfaz de Usuario

#### Página de Productos - Configuración
```
┌────────────────────────────────────────────────┐
│ Producto: Pasión Roja                          │
│ [Editar Colores y Flores] 🎨                   │
├────────────────────────────────────────────────┤
│ Colores Definidos:                             │
│                                                │
│ 1. 🔴 Rojo (12 flores)                         │
│    Flores disponibles:                         │
│    • Rosa roja (predeterminada)                │
│    • Clavel rojo                               │
│    • Gerbera roja                              │
│    [+ Agregar flor]                            │
│                                                │
│ 2. 🟢 Verde oscuro (5 flores)                  │
│    Flores disponibles:                         │
│    • Eucalipto (predeterminada)                │
│    [+ Agregar flor]                            │
│                                                │
│ [+ Agregar Color]                              │
└────────────────────────────────────────────────┘
```

#### Crear Pedido - Selección de Flores
```
┌────────────────────────────────────────────────┐
│ Nuevo Pedido - Paso 2: Seleccionar Flores     │
├────────────────────────────────────────────────┤
│ Producto: Pasión Roja                          │
│                                                │
│ 🔴 Color Rojo:                                 │
│ ┌──────────────────────────────────────────┐  │
│ │ Flor: [Rosa roja (12 disponible) ▼]     │  │
│ │ Cantidad: [ 12 ] tallos                  │  │
│ │ Stock suficiente ✓                       │  │
│ └──────────────────────────────────────────┘  │
│                                                │
│ 🟢 Color Verde oscuro:                         │
│ ┌──────────────────────────────────────────┐  │
│ │ Flor: [Eucalipto (200 disponible) ▼]    │  │
│ │ Cantidad: [ 5 ] ramas                    │  │
│ │ Stock suficiente ✓                       │  │
│ └──────────────────────────────────────────┘  │
│                                                │
│ 🏺 Contenedor:                                 │
│ ┌──────────────────────────────────────────┐  │
│ │ [Florero vidrio mediano (22 disponible)]│  │
│ │ Cantidad: [ 1 ]                          │  │
│ └──────────────────────────────────────────┘  │
│                                                │
│ Costo Estimado: $18,500                       │
│ (12 x $1,500 + 5 x $500 + 1 x $2,500)         │
│                                                │
│ [← Volver] [Continuar →]                      │
└────────────────────────────────────────────────┘
```

### 6. Migración de Datos Existentes

Para productos actuales que tienen texto simple:
```python
# De:
producto.flores_asociadas = "Rosa roja, Clavel rojo, Eucalipto"
producto.colores_asociados = "Rojo, Verde oscuro, Burdeo"

# A:
Crear automáticamente:
  - Color "Rojo" → Flores: Rosa roja, Clavel rojo
  - Color "Verde oscuro" → Flores: Eucalipto
  - Color "Burdeo" → Flores: Rosa roja (tentativo)
```

---

## 🚀 Implementación

¿Quieres que implemente este sistema completo? Incluiría:

1. ✅ Nuevas tablas en la base de datos
2. ✅ Modelos SQLAlchemy
3. ✅ API endpoints para configurar colores y flores
4. ✅ Interfaz para configurar productos
5. ✅ Interfaz mejorada para crear pedidos
6. ✅ Script de migración de datos existentes

**¿Procedemos con la implementación?** 🌸

