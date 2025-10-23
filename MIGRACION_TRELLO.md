# 🔄 Guía de Migración desde Trello a Las-Lira

## 📊 Sistema Actual vs Sistema Nuevo

### Flujo de Estados (IDÉNTICO)

```
Trello Actual          →  Sistema Las-Lira
─────────────────────────────────────────────
PEDIDO                 →  Pedido
Pedidos Semana         →  Pedidos Semana  
ENTREGAS PARA MAÑANA   →  Entregas para Mañana
Entregas de hoy        →  Entregas de Hoy
En Proceso             →  En Proceso
Listo para despacho    →  Listo para Despacho
Despachados            →  Despachados
```

### Sistema de Etiquetas (IDÉNTICO)

#### 🗓️ Días de la Semana
- 🟡 LUNES (amarillo)
- 🟠 MARTES (naranja)
- 🔴 MIERCOLES (rojo)
- 🟣 JUEVES (morado)
- 🔵 VIERNES (azul)
- 🟦 SABADO (cyan)
- 🟢 DOMINGO (verde)

#### 💰 Estado de Pago
- 🟢 PAGADO (verde)
- 🔴 NO PAGADO (rojo)
- 🟠 FALTA BOLETA o FACTURA (naranja)

#### 📌 Tipo de Pedido
- ⚫ EVENTO
- MANTENCIONES

---

## 📁 Estructura de Datos

### Datos Extraídos de Tu Trello

Tienes **6,456 pedidos** en el historial desde agosto 2022 hasta octubre 2025.

**Campos que ya tienes:**
- ✅ fecha
- ✅ canal (WhatsApp/Shopify)
- ✅ n_pedido (número de Shopify)
- ✅ cliente
- ✅ celular
- ✅ producto
- ✅ precio
- ✅ envio
- ✅ para
- ✅ mensaje
- ✅ firma
- ✅ direccion
- ✅ cobranza (BOLETA/FACTURA)

### Campos del Sistema Las-Lira

**Campos que coinciden 100%:**
```
Trello                  →  Las-Lira
─────────────────────────────────────
fecha                   →  fecha_pedido
cliente                 →  cliente_nombre
celular                 →  cliente_telefono
producto                →  arreglo_pedido
precio                  →  precio_ramo
envio                   →  precio_envio
para                    →  destinatario
mensaje                 →  mensaje
firma                   →  firma
direccion               →  direccion_entrega
cobranza                →  cobranza
n_pedido (Shopify)      →  shopify_order_number
canal                   →  canal
```

**Campos nuevos en Las-Lira:**
- `dia_entrega`: LUNES, MARTES, etc. (se puede calcular automáticamente)
- `estado_pago`: Pagado/No Pagado/Falta Boleta (extraer de etiquetas)
- `tipo_pedido`: EVENTO/MANTENCIONES (extraer de etiquetas)
- `estado`: Pedido/En Proceso/etc. (extraer de columna de Trello)
- `motivo`: Cumpleaños, Aniversario, etc. (opcional)
- `foto_enviado_url`: Foto de trazabilidad (nueva funcionalidad)

---

## 🔧 Proceso de Migración

### Opción 1: Migración Automática (Recomendada)

Creamos un script que:
1. Lee tu JSON/CSV exportado del Trello
2. Mapea los campos automáticamente
3. Calcula el día de la semana desde la fecha
4. Importa todo a la base de datos

```bash
python scripts/migrar_desde_trello.py tu_archivo.json
```

### Opción 2: Importar Excel

Si prefieres Excel:
1. Exporta tu data de Trello a CSV
2. Abre el archivo `04_Pedidos.xlsx` del sistema
3. Copia y pega los datos siguiendo el formato
4. Importa con el script:

```bash
python scripts/importar_excel.py 04_Pedidos.xlsx
```

### Opción 3: Migración Manual por Archivos Mensuales

Como tienes los pedidos organizados por mes (agosto 2022 - octubre 2025):

1. Exportar cada tabla de Trello a JSON/CSV
2. Ejecutar migración por lotes:

```bash
python scripts/migrar_por_lotes.py carpeta_archivos_mensuales/
```

---

## 📸 Fotos de Pedidos

### En el Trello
- Fotos están como adjuntos en cada tarjeta
- Ej: "imagen.jpeg" en la sección de Archivos

### En Las-Lira
El sistema puede:
1. **Descargar automáticamente** las fotos del Trello
2. **Subirlas manualmente** desde tu computador
3. **Vincularlas** por URL si están en Google Drive

**Estructura de fotos:**
```
backend/uploads/
  ├── productos/
  │   ├── passion-roja.jpg
  │   └── jardin-primaveral.jpg
  └── pedidos/
      ├── ped001_enviado.jpg
      └── ped002_enviado.jpg
```

---

## 🎯 Plan de Migración Recomendado

### Fase 1: Migración de Base (1 día)
1. ✅ Importar productos del catálogo
2. ✅ Importar inventario de flores y contenedores
3. ✅ Importar proveedores

### Fase 2: Historial de Pedidos (2 días)
1. ✅ Migrar pedidos archivados (2022-2024) → Estado "Archivado"
2. ✅ Migrar pedidos de 2025 → Estados correspondientes
3. ✅ Validar que todo se importó correctamente

### Fase 3: Pedidos Activos (1 día)
1. ✅ Importar pedidos actuales del Trello
2. ✅ Verificar estados y etiquetas
3. ✅ Descargar fotos de pedidos activos

### Fase 4: Pruebas Paralelas (1 semana)
1. ✅ Usar Trello y Las-Lira en paralelo
2. ✅ Crear pedidos nuevos en ambos sistemas
3. ✅ Comparar y ajustar

### Fase 5: Transición Completa (1 día)
1. ✅ Migración final de pedidos pendientes
2. ✅ Archivar Trello
3. ✅ Usar solo Las-Lira

---

## 📊 Ejemplo de Migración

### Tarjeta del Trello:
```
MARIANA SERRA C. / 9.694 1497
Etiquetas: LUNES, NO PAGADO

Descripción:
PEONIAS (10)
$40.000+ $7.000 envío

PARA: Sra Paula Silva Dittborn
MENSAJE: Feliz cumpleaños! Gracias por cuidar a la Abuela
FIRMA: Familia Serra Cambiaso

DIRECCIÓN
Camino la Fuente interior 2767
Las condes

BOLETA
Tr. 20/10/25

Archivos:
- imagen.jpeg (foto del arreglo)
```

### Resultado en Las-Lira:
```json
{
  "cliente_nombre": "MARIANA SERRA C.",
  "cliente_telefono": "9.694 1497",
  "arreglo_pedido": "PEONIAS (10)",
  "precio_ramo": 40000,
  "precio_envio": 7000,
  "destinatario": "Sra Paula Silva Dittborn",
  "mensaje": "Feliz cumpleaños! Gracias por cuidar a la Abuela",
  "firma": "Familia Serra Cambiaso",
  "direccion_entrega": "Camino la Fuente interior 2767, Las condes",
  "cobranza": "BOLETA Tr. 20/10/25",
  "dia_entrega": "LUNES",
  "estado_pago": "No Pagado",
  "producto_imagen": "imagen.jpeg"
}
```

---

## 🛠️ Scripts de Migración

### Script 1: Analizar JSON del Trello
```bash
python scripts/analizar_trello_json.py export_trello.json
```
**Output:**
- Total de pedidos encontrados
- Estados detectados
- Etiquetas encontradas
- Campos faltantes

### Script 2: Migración Completa
```bash
python scripts/migrar_trello_completo.py export_trello.json --con-fotos
```

### Script 3: Descargar Fotos
```bash
python scripts/descargar_fotos_trello.py export_trello.json
```

---

## ✅ Checklist de Migración

### Antes de Migrar
- [ ] Hacer backup del Trello (exportar a JSON)
- [ ] Descargar todas las fotos de pedidos activos
- [ ] Verificar que todas las columnas están mapeadas
- [ ] Probar con 10 pedidos de ejemplo

### Durante la Migración
- [ ] Migrar productos y catálogo
- [ ] Migrar inventario
- [ ] Migrar pedidos históricos (archivados)
- [ ] Migrar pedidos activos
- [ ] Subir fotos
- [ ] Verificar etiquetas y estados

### Después de Migrar
- [ ] Verificar conteo de pedidos (6,456 total)
- [ ] Probar tablero Kanban
- [ ] Verificar que las fotos se ven correctamente
- [ ] Probar mover pedidos entre estados
- [ ] Crear un pedido de prueba nuevo

---

## 🆘 Preguntas Frecuentes

### ¿Se perderá alguna información?
No. El sistema Las-Lira tiene TODOS los campos del Trello + funcionalidades adicionales.

### ¿Qué pasa con las fotos?
Las fotos se migran automáticamente o se pueden subir manualmente. El sistema mantiene la trazabilidad.

### ¿Puedo seguir usando Trello mientras pruebo?
Sí. Recomendamos usar ambos en paralelo por 1 semana antes de la transición completa.

### ¿Qué pasa con los pedidos archivados?
Se migran con estado "Archivado" para mantener el historial pero no aparecen en el tablero activo.

### ¿Cómo migro 6,456 pedidos?
Con el script automático. Toma aproximadamente 10-15 minutos para toda la data.

---

## 📞 Soporte

Si necesitas ayuda con la migración:
1. Revisa los logs: `logs/migracion.log`
2. Verifica errores: `logs/errores.log`
3. Consulta la documentación: `DATABASE_DESIGN.md`

---

**Fecha de creación:** Octubre 2025  
**Última actualización:** Octubre 2025  
**Estado:** Lista para migración 🚀

