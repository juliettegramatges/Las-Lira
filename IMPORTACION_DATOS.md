# 📊 Importación de Datos Históricos - Las Lira

## Descripción

Este documento describe cómo importar todos los datos históricos de Trello al sistema web de Las Lira.

## 📦 Archivos de Datos

Los siguientes archivos CSV contienen los datos procesados y listos para importar:

### ✅ Archivos Disponibles

1. **`base_clientes_completa.csv`** (2,857 clientes)
   - Información completa de clientes
   - Historial de compras y segmentación
   - Contactos y direcciones

2. **`pedidos_trello_COMPLETO.csv`** (8,685 pedidos)
   - Todos los pedidos históricos desde 2022
   - Información de productos, insumos, precios
   - Estados de pago y entrega

3. **`catalogo_productos_completo.csv`** (188 productos)
   - Catálogo completo con variantes
   - Precios, dimensiones, cuidados

4. **`insumos_las_lira.csv`** (129 insumos)
   - Flores, contenedores, follajes
   - Ubicaciones y categorías

---

## 🚀 Proceso de Importación

### Opción 1: Recrear Base de Datos (RECOMENDADO)

Si es la primera vez o quieres empezar desde cero:

```bash
# 1. Entrar al directorio backend
cd backend

# 2. Activar entorno virtual
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Recrear base de datos
python << 'EOF'
from app import app, db
with app.app_context():
    db.drop_all()
    db.create_all()
    print("✅ Base de datos recreada")
EOF

# 4. Importar datos históricos
python scripts/importar_datos_historicos.py
```

### Opción 2: Migrar Base de Datos Existente

Si ya tienes datos y quieres agregar los históricos:

```bash
# 1. Entrar al directorio backend
cd backend

# 2. Activar entorno virtual
source venv/bin/activate

# 3. Ejecutar migración
python scripts/migrar_base_datos.py

# 4. Importar datos históricos
python scripts/importar_datos_historicos.py
```

---

## 📋 Estructura de Datos Importados

### 👥 Clientes (2,857)

```python
{
    'id': 'CLI_0001',
    'nombre': 'Nombre del cliente',
    'telefono': '+56912345678',
    'email': 'cliente@email.com',
    'tipo_cliente': 'VIP',  # VIP, Fiel, Ocasional, Nuevo
    'direccion_principal': 'Dirección',
    'total_pedidos': 10,
    'total_gastado': 1500000,
    'fecha_registro': '2022-01-15',
    'ultima_compra': '2024-10-20'
}
```

### 📦 Pedidos (8,685)

```python
{
    'id': 'PED-00001',
    'fecha_pedido': '2022-07-27',
    'fecha_entrega': '2022-07-28',
    'canal': 'WhatsApp',  # o 'Shopify'
    'cliente_id': 'CLI_0001',
    'cliente_nombre': 'Nombre del cliente',
    'arreglo_pedido': 'Bouquet',
    'precio_ramo': 65000,
    'precio_envio': 7000,
    'direccion_entrega': 'Dirección completa',
    'comuna': 'Las Condes',
    'estado': 'Archivado',  # o 'Activo'
    'estado_pago': 'Pagado',  # o 'Pendiente'
    'motivo': 'Cumpleaños',
    'insumos_extraidos': 'ROSAS: 20, LILIUMS: 5',
    'dimensiones': '40×50 cm',
    'contenedor': 'Florero',
    'colores': 'Rosado, Blanco'
}
```

---

## 📊 Estadísticas de Importación Esperadas

### Clientes
- Total: 2,857 clientes únicos
- VIP: 109 (3.8%)
- Premium/Fiel: 295 (10.3%)
- Otros: 2,453 (85.9%)

### Pedidos
- Total: 8,685 pedidos
- Archivados: 8,357 (96.2%)
- Activos: 328 (3.8%)
- Pagados: 8,574 (98.7%)

### Distribución por Año
- 2022: 1,161 pedidos
- 2023: 2,441 pedidos
- 2024: 2,866 pedidos
- 2025: 2,217 pedidos

---

## ⚠️ Notas Importantes

### Datos Vacíos o Nulos

El script maneja automáticamente datos vacíos o nulos:
- Teléfonos faltantes → `SIN_TEL_XXXX`
- Direcciones vacías → `Sin dirección`
- Emails vacíos → `None`
- Fechas inválidas → `datetime.now()`

### Relaciones

- **Cliente ↔ Pedidos**: Automática por `cliente_id`
- **Pedido ↔ Producto**: Por ahora `arreglo_pedido` contiene el nombre
- **Pedido ↔ Insumos**: Campo `insumos_extraidos` con texto

### Personalización de Importación

Puedes modificar el script `importar_datos_historicos.py` para:
- Filtrar pedidos por fecha
- Importar solo ciertos clientes
- Ajustar mapeos de campos
- Agregar validaciones adicionales

---

## 🔧 Solución de Problemas

### Error: "Column already exists"
✅ Normal, significa que la columna ya estaba creada.

### Error: "Duplicate key value"
❌ Ya existe un registro con ese ID. Opciones:
- Limpiar la tabla antes: `db.drop_all(); db.create_all()`
- Modificar el script para actualizar en vez de crear

### Error: "Invalid datetime format"
⚠️ Algunas fechas en el CSV pueden tener formato incorrecto.
- El script intenta múltiples formatos automáticamente
- Las fechas inválidas se reemplazan con la fecha actual

### La importación es muy lenta
💡 Normal con 8,685 pedidos. Tiempo estimado: 2-5 minutos

---

## 📈 Verificación Post-Importación

Después de importar, verifica en el sistema web:

1. **Dashboard de Clientes**
   - Total de clientes: ~2,857
   - Segmentación correcta (VIP, Premium, etc.)

2. **Dashboard de Pedidos**
   - Total de pedidos: ~8,685
   - Filtros por estado funcionando
   - Fechas correctas

3. **Relaciones**
   - Los pedidos muestran el cliente correcto
   - Los totales del cliente coinciden

---

## 🎯 Próximos Pasos

Después de la importación exitosa:

1. ✅ Verificar datos en el sistema web
2. ✅ Importar productos e insumos (si aún no están)
3. ✅ Crear relaciones Pedido ↔ Producto (si aplicable)
4. ✅ Configurar permisos y accesos
5. ✅ Capacitar al equipo en el nuevo sistema

---

## 💾 Respaldos

**IMPORTANTE**: Antes de importar, crea un respaldo:

```bash
# Respaldar base de datos SQLite
cp backend/instance/las_lira.db backend/instance/las_lira_backup_$(date +%Y%m%d).db

# O si usas PostgreSQL
pg_dump las_lira > backup_$(date +%Y%m%d).sql
```

---

## 📞 Soporte

Si encuentras algún problema durante la importación:
1. Revisa los logs del script
2. Verifica que los archivos CSV estén en la raíz del proyecto
3. Asegúrate de tener las dependencias instaladas
4. Consulta este documento para soluciones comunes

---

**¡Listo para comenzar! 🚀**


