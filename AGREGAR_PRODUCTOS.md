# 📦 Cómo Agregar el Producto "Personalización"

## ✅ Método 1: Script Automático (Recomendado)

Abre una **terminal nueva** (fuera de Cursor) y ejecuta:

```bash
cd /Users/juliettegramatges/Las-Lira/backend
python3 scripts/agregar_personalizacion.py
```

**Resultado esperado:**
```
🌸 Agregando producto 'Personalización'...
✅ Producto 'Personalización' creado exitosamente (ID: X)

📦 Total de productos en la base de datos: XX
```

---

## 🔄 Método 2: Importar TODO el Catálogo

Si quieres importar **todos los productos** del `catalogo_productos_completo.csv`:

```bash
cd /Users/juliettegramatges/Las-Lira/backend
python3 scripts/importar_productos_catalogo.py
```

Este script:
- ✅ Lee el CSV completo
- ✅ Crea productos nuevos
- ✅ Actualiza productos existentes
- ✅ Extrae precios automáticamente

---

## ⚠️ Si tienes error "Segmentation Fault"

Esto puede pasar en macOS con ciertas versiones de Python/SQLite.

### Solución A: Usar Python del sistema

```bash
/usr/bin/python3 scripts/agregar_personalizacion.py
```

### Solución B: Reinstalar SQLite

```bash
brew reinstall sqlite
```

### Solución C: Agregar manualmente desde el frontend

1. Abre el sistema web
2. Ve a **"Productos"**
3. Busca si hay un botón de **"Crear Producto"** o similar
4. Si no existe, necesitas agregarlo temporalmente con SQL directo

---

## 🛠️ Método 3: SQL Directo (Última opción)

Si nada funciona, ejecuta esto en tu base de datos:

```bash
cd /Users/juliettegramatges/Las-Lira/backend
sqlite3 laslira.db
```

Luego dentro de SQLite:

```sql
INSERT INTO productos (nombre, descripcion, categoria, tipo_arreglo, precio_venta, activo)
VALUES ('Personalización', 'Arreglo personalizado según las preferencias del cliente', 'Flores en Plantas', 'Ramo', 0, 1);

SELECT * FROM productos WHERE nombre = 'Personalización';
.exit
```

---

## 🎯 Verificar que funciona

1. Reinicia el **backend** (si estaba corriendo)
2. Refresca el **frontend**
3. Abre "Nuevo Pedido"
4. En el dropdown "Producto de Catálogo" deberías ver:
   - ✅ **Personalización - $0**

5. Cuando lo selecciones, aparecerá:
   - 🎨 Campo "Producto en Shopify Parecido"
   - 📦 Bloque de insumos vacío

---

## 📞 ¿Necesitas ayuda?

Si ninguno de estos métodos funciona, dime:
1. ¿Qué error específico sale?
2. ¿Qué versión de Python tienes? (`python3 --version`)
3. ¿El backend está corriendo correctamente?


