# 📋 Procesamiento de Datos de Trello

Este documento explica cómo extraer y limpiar los datos de Trello para generar el archivo final de pedidos.

## 📂 Archivos

### 🔹 Archivos de Entrada
- **`ryFivJoh - las-lira-gestion.json`**: Exportación JSON de Trello (archivo fuente)

### 🔹 Script de Procesamiento
- **`extraer_y_limpiar_trello.py`**: Script único que extrae del JSON y aplica todas las limpiezas

### 🔹 Archivos de Salida
- **`pedidos_trello_COMPLETO.csv`**: Archivo final con todos los pedidos limpios (8,685 pedidos)
- **`eventos_trello.csv`**: Eventos extraídos del Trello (78 eventos)

---

## 🚀 Uso

### Ejecutar el script completo:

```bash
python3 extraer_y_limpiar_trello.py
```

Este script realiza automáticamente:
1. ✅ Extrae datos del JSON de Trello
2. ✅ Normaliza teléfonos
3. ✅ Limpia nombres de clientes (title case, sin sufijos)
4. ✅ **Separa teléfonos pegados a nombres** (ej: "Yamily Bustamante +56 9 9828")
5. ✅ Extrae emails
6. ✅ **Separa nombres pegados a emails** (ej: "Monica Vergara monicavergara123@gmail.com")
7. ✅ Separa detalles (paréntesis, guiones)
8. ✅ Identifica pedidos Shopify
9. ✅ Reubicar datos incorrectos en columnas
10. ✅ Completa teléfonos faltantes
11. ✅ Normaliza precios (agrega 000 cuando corresponde)
12. ✅ **Limpia y estandariza productos**
13. ✅ **Extrae links de productos** (nueva columna)
14. ✅ **Elimina precios del nombre del producto**
15. ✅ **Extrae tamaños de productos mejorado** (XS, S, M, L, XL, XXL)
16. ✅ **Extrae dimensiones** (ancho x alto x profundidad)
17. ✅ **Extrae cantidad de flores/rosas** (notas_insumos)
18. ✅ Identifica comunas
19. ✅ Separa tipo de documento (BOLETA/FACTURA) y método de pago (TRANSFERENCIA/BICE/EFECTIVO)
20. ✅ Actualiza estado de pago para 2022
21. ✅ Asigna IDs únicos cronológicos

---

## 📊 Estructura del Archivo Final

El archivo `pedidos_trello_COMPLETO.csv` contiene las siguientes columnas:

| Columna | Descripción |
|---------|-------------|
| `id_pedido` | ID único secuencial (PED-00001, PED-00002...) |
| `fecha_creacion` | Fecha de creación (extraída del ID de Trello) |
| `fecha_entrega` | Fecha de entrega programada |
| `canal` | Canal de venta (WhatsApp, Shopify) |
| `n_pedido` | Número de pedido (si es Shopify) |
| `cliente` | Nombre del cliente (normalizado, title case) |
| `contacto` | Teléfono o información de contacto normalizada (+569 XXXX XXXX) |
| `correo_cliente` | Email del cliente |
| `detalles_cliente` | Información adicional (notas, alias, etc) |
| `producto` | Descripción original del producto |
| `producto_limpio` | Producto sin dimensiones, precios ni links |
| `tipo_arreglo` | Categoría del arreglo (DIFUNTO, BOUQUET, CENTRO DE MESA, etc) |
| `tipo_contenedor` | Tipo de recipiente (VIDRIO, CANASTO, PAILA, FRUTERA, MATERO, etc) |
| `colores` | Lista de colores separados por comas |
| `flores` | Lista de flores y follajes separados por comas |
| `cantidad_flores` | Cantidad de flores si está especificada (ej: 20, 50) |
| `dimensiones_alto` | Alto en cm |
| `dimensiones_ancho` | Ancho en cm |
| `dimensiones_profundidad` | Profundidad en cm (si aplica) |
| `link` | Links extraídos del producto (URLs de Shopify, etc) |
| `precio` | Precio normalizado |
| `envio` | Costo de envío normalizado |
| `para` | Destinatario del producto |
| `mensaje` | Mensaje en tarjeta |
| `firma` | Firma en tarjeta |
| `direccion` | Dirección de entrega |
| `notas_cobranza` | Información de cobranza y pagos |
| `tipo_documento` | Tipo de documento (BOLETA, FACTURA) |
| `metodo_pago` | Método de pago (TRANSFERENCIA, BICE, EFECTIVO, etc) |
| `pagado` | Estado de pago (PAGADO, NO PAGADO, SIN ETIQUETA) |
| `tamaño` | Tamaño del producto (XS, S, M, L, XL, XXL) |
| `dimensiones` | Dimensiones extraídas (ancho x alto o ancho x alto x prof) |
| `notas_insumos` | Cantidad de flores/rosas especificadas en el producto |
| `comuna` | Comuna extraída de la dirección |

---

## 📈 Estadísticas del Archivo Final

- **Total de pedidos**: 8,685
- **Con teléfono**: 6,464 (74.4%)
- **Con email**: 11 (0.1%)
- **Con comuna**: 5,290 (60.9%)
- **Con tamaño**: 1,376 (15.8%)
- **Con dimensiones**: 927 (10.7%)
- **Con notas de insumos**: 122 (1.4%)
- **Con tipo documento**: 8,115 (93.4%)
- **Con método pago**: 5,229 (60.2%)

---

## 🔧 Modificar el Script

Si necesitas agregar nuevas limpiezas o modificar las existentes, edita el archivo `extraer_y_limpiar_trello.py`.

Las funciones de limpieza están organizadas en la sección **FUNCIONES DE LIMPIEZA** del script (líneas 17-249).

---

## ⚠️ Notas Importantes

1. **No borrar el archivo JSON original**: Es la fuente de datos y puede necesitarse para re-procesar.
2. **El script sobrescribe los archivos de salida**: Si ejecutas el script nuevamente, se regenerarán los archivos CSV.
3. **IDs cronológicos**: Los IDs se asignan en orden de `fecha_creacion`. Pedidos multi-línea del mismo cliente y fecha comparten el mismo ID.

---

## 📝 Historial de Cambios

- **2025-10-24 (v7)**: Análisis detallado y estructurado de productos
  - Nueva función `analizar_producto_detallado()`
  - Extrae tipo de arreglo (DIFUNTO, BOUQUET, CENTRO DE MESA, etc)
  - Extrae tipo de contenedor (VIDRIO, CANASTO, PAILA, FRUTERA, etc)
  - Extrae colores como lista (BLANCO, VERDE, AZUL, BURGUNDY, etc)
  - Extrae flores y follajes (ROSAS, PEONÍAS, LILIUM, EUCALIPTO, etc)
  - Extrae cantidad de flores cuando está especificada
  - Extrae dimensiones estructuradas (alto, ancho, profundidad)
  - Producto limpio sin dimensiones, precios ni links
  - Nuevas columnas: `producto_limpio`, `tipo_arreglo`, `tipo_contenedor`, 
    `colores`, `flores`, `cantidad_flores`, `dimensiones_alto`, 
    `dimensiones_ancho`, `dimensiones_profundidad`
  - Total columnas: 34
  - Cobertura: 26.5% tipo arreglo, 34.3% contenedor, 37.1% colores, 10.7% flores

- **2025-10-24 (v6)**: Limpieza y estandarización de productos
  - Nueva función `limpiar_y_estandarizar_producto()`
  - Estandariza "MANTENCIÓN SEMANAL" (412 productos)
  - Extrae links de URLs (59 productos) a nueva columna `link`
  - Elimina precios del nombre del producto (99.97% limpiado)
  - Nueva columna: `link`
  - Total columnas: 25

- **2025-10-24 (v5)**: Extracción mejorada de tamaños e insumos
  - Nueva función `extract_size_info()` mucho más completa
  - Extrae tamaños (XS, S, M, L, XL, XXL) desde múltiples fuentes
  - Extrae dimensiones (20x30, 15x20x10 cms)
  - Extrae cantidad de rosas y otras flores (notas_insumos)
  - Eliminada columna `tamaño_original`, agregadas `dimensiones` y `notas_insumos`
  - Cobertura mejorada: 14.2% → 15.8% con tamaño, +10.7% con dimensiones, +1.4% con notas

- **2025-10-24 (v4)**: Agregada separación de nombres pegados a emails
  - Nueva función `separar_nombre_de_email()`
  - Detecta y separa patrones como "Monica Vergara monicavergara123@gmail.com"
  - Mejora limpieza de columnas de cliente y correo_cliente

- **2025-10-24 (v3)**: Renombradas columnas para mayor claridad
  - `celular` → `contacto` (puede contener otros detalles de contacto)
  - `cobranza` → `notas_cobranza` (más descriptivo)

- **2025-10-24 (v2)**: Agregada separación de teléfonos pegados a nombres
  - Nueva función `separar_telefono_de_nombre()` 
  - Detecta y separa patrones como "Yamily Bustamante +56 9 9828"
  - Recuperados 37 teléfonos adicionales (74.0% → 74.4% cobertura)

- **2025-10-24 (v1)**: Creación del script único con todas las limpiezas integradas
  - Extracción de JSON de Trello
  - Normalización de teléfonos, nombres, precios
  - Extracción de emails, comunas, tamaños
  - Separación de tipo_documento y metodo_pago
  - Asignación de IDs únicos cronológicos

