# 📚 Guía de Scripts de Procesamiento

## 🗂️ Archivos Disponibles

### 1. **`extraer_y_limpiar_trello.py`** (Script completo)
Extrae datos del JSON de Trello y aplica todas las limpiezas.

**Cuándo usar:**
- Cuando tienes un nuevo JSON de Trello
- Cuando necesitas regenerar todo desde cero
- Primera vez que procesas los datos

**Tiempo:** ~30-60 segundos

**Comando:**
```bash
python3 extraer_y_limpiar_trello.py
```

**Genera:**
- `pedidos_trello_COMPLETO.csv` (con todas las limpiezas + análisis)
- `eventos_trello.csv`

---

### 2. **`analizar_productos.py`** (Solo análisis de productos)
Analiza únicamente la columna `producto` del CSV existente.

**Cuándo usar:**
- Ya tienes `pedidos_trello_COMPLETO.csv`
- Quieres refinar el análisis de productos
- Quieres probar nuevas categorías o patrones
- Cambios rápidos sin regenerar todo

**Tiempo:** ~5-10 segundos

**Comando:**
```bash
python3 analizar_productos.py
```

**Modifica:**
- `pedidos_trello_COMPLETO.csv` (actualiza solo las columnas de análisis)

---

## 🔄 Flujo de Trabajo Recomendado

### Primera vez:
```bash
# 1. Extraer y limpiar todo desde el JSON
python3 extraer_y_limpiar_trello.py
```

### Iteraciones posteriores (solo productos):
```bash
# 2. Refinar análisis de productos
# (puedes editar analizar_productos.py y ejecutar múltiples veces)
python3 analizar_productos.py
```

---

## 📊 Columnas Generadas por `analizar_productos.py`

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| `producto_limpio` | Nombre sin dimensiones/precios/links | "BOUQUET CON ROSAS NARANJAS" |
| `tipo_arreglo` | Categoría del arreglo | "BOUQUET", "DIFUNTO", "CENTRO DE MESA" |
| `tipo_contenedor` | Tipo de recipiente | "VIDRIO", "CANASTO", "PAILA", "FRUTERA" |
| `colores` | Lista de colores (separados por comas) | "BLANCO, VERDE, AZUL" |
| `flores` | Lista de flores (separados por comas) | "ROSAS, PEONÍAS, EUCALIPTO" |
| `cantidad_flores` | Cantidad si está especificada | "20", "50" |
| `dimensiones_alto` | Alto en cm | "65" |
| `dimensiones_ancho` | Ancho en cm | "50" |
| `dimensiones_profundidad` | Profundidad en cm | "30" |

---

## ✏️ Personalizar el Análisis

Para agregar nuevos tipos, contenedores, colores o flores:

1. Abre `analizar_productos.py`
2. Busca la sección correspondiente (ej: `# 1. TIPO DE ARREGLO`)
3. Agrega tu nuevo patrón:

```python
# Ejemplo: agregar nuevo tipo de arreglo
tipos_arreglo = [
    (r'DIFUNTO|FUNERARIO|SOBRE URNA', 'DIFUNTO'),
    (r'BOUQUET|RAMO', 'BOUQUET'),
    (r'TU_NUEVO_PATRON', 'TU_CATEGORIA'),  # ⬅️ Agregar aquí
    # ...
]
```

4. Guarda y ejecuta:
```bash
python3 analizar_productos.py
```

---

## 🎯 Categorías Disponibles

### Tipos de Arreglo:
- DIFUNTO
- BOUQUET
- ARREGLO FLORAL
- MANTENCIÓN SEMANAL
- CENTRO DE MESA
- NACIMIENTO
- MATRIMONIO
- CUMPLEAÑOS

### Contenedores:
- VIDRIO, CANASTO, PAILA, FRUTERA, MATERO
- FLORERO, CILINDRO, CUBO, CAJA, BOÎTE
- HELADERA, AMPOLLETA

### Colores:
- BLANCO, ROJO, ROSADO, AZUL, VERDE
- AMARILLO, NARANJA, MORADO, LILA, FUCSIA
- BURGUNDY, PASTEL, COLORIDO

### Flores:
- ROSAS, PEONÍAS, LILIUM, TULIPANES, ORQUÍDEAS
- LISIANTHUS, HORTENSIAS, CLAVELES, GIRASOLES
- MARGARITAS, GERBERAS, CALAS, ALSTROMERIAS
- EUCALIPTO, RUSCO (follajes)

---

## 📈 Estadísticas Típicas

Cobertura del análisis (sobre 8,685 pedidos):

| Campo | Cobertura |
|-------|-----------|
| Tipo de arreglo | 26.5% (2,302 productos) |
| Contenedor | 34.3% (2,982 productos) |
| Colores | 37.1% (3,222 productos) |
| Flores | 10.7% (928 productos) |
| Dimensiones | 10.7% (927 productos) |

---

## 💡 Tips

1. **Iteración rápida**: Usa `analizar_productos.py` para probar cambios sin esperar
2. **Backup**: Haz copia del CSV antes de cambios grandes
3. **Patrones regex**: Los patrones usan expresiones regulares de Python
4. **Case insensitive**: Todos los patrones ignoran mayúsculas/minúsculas
5. **Múltiples valores**: Colores y flores se guardan como lista separada por comas

---

## 🆘 Solución de Problemas

**"No se encuentra el archivo"**
```bash
# Asegúrate de estar en el directorio correcto
cd /Users/juliettegramatges/Las-Lira
```

**"Permission denied"**
```bash
# Dale permisos de ejecución
chmod +x analizar_productos.py
```

**"Resultados inesperados"**
- Revisa los patrones regex en el script
- Prueba con un CSV pequeño primero
- Verifica que el CSV tenga la columna `producto`

---

## 📝 Notas

- `analizar_productos.py` sobrescribe las columnas de análisis existentes
- El script es idempotente (puedes ejecutarlo múltiples veces)
- No afecta las otras columnas del CSV (cliente, precio, etc.)
- Es ~6x más rápido que regenerar todo desde el JSON

---

✨ **¡Listo para analizar productos!** 🌸


