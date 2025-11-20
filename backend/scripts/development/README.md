# Scripts de Desarrollo y Prueba

Esta carpeta contiene scripts utilizados durante el desarrollo y testing del sistema. **No son necesarios para el funcionamiento en producción**.

## Contenido

### Scripts de Productos y Shopify
- `actualizar_imagenes_productos.py` - Actualiza URLs de imágenes de productos
- `actualizar_tabla_productos.py` - Migración de tabla de productos
- `asociar_productos_existentes.py` - Asocia productos del sistema con Shopify
- `consolidar_catalogos.py` - Consolida catálogos de productos
- `corregir_imagenes.py` - Correcciones de URLs de imágenes
- `extraer_productos_shopify.py` - Extrae productos desde Shopify API
- `integrar_productos_sistema.py` - Integra productos en el sistema
- `sincronizar_productos.py` - Sincroniza productos con Shopify
- `verificar_consolidacion.py` - Verifica consolidación de catálogos
- `verificar_estado_productos.py` - Verifica estado de productos en BD

### Scripts de Prueba y Testing
- `probar_conexion_db.py` - Prueba conexión a base de datos
- `probar_endpoint_productos.py` - Prueba endpoints de productos
- `probar_productos.py` - Prueba funcionalidad de productos
- `test_flujo_insumos_corregido.py` - Test de flujo de insumos
- `test_reserva_insumos.py` - Test de reserva de inventario

### Scripts de Migración
- `migrar_foto_respaldo.py` - Migración de fotos de respaldo

## Uso

Estos scripts se ejecutan manualmente desde la línea de comandos cuando es necesario:

```bash
cd backend/scripts/development
python nombre_del_script.py
```

**Nota:** La mayoría de estos scripts son de uso único o para debugging. No están integrados en el flujo normal de la aplicación.
