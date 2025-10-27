# 🏷️ Sistema de Etiquetas Múltiples y Eventos - Las Lira

## 🎯 RESUMEN EJECUTIVO

Se ha implementado un **sistema completo de etiquetas múltiples** para clientes y **detección automática de eventos** que elimina el sesgo del sistema anterior donde clientes "VIP" eran simplemente aquellos que compraban para eventos.

---

## 📊 PROBLEMA RESUELTO

### **Antes:**
- Cliente "VIP" = Cliente que gasta mucho
- **Sesgo**: Un cliente que compra 1 evento grande era "VIP", pero un cliente frecuente que compra flores individuales no

### **Ahora:**
- **Sistema de 6 dimensiones** con múltiples etiquetas
- Cada cliente puede tener **6+ etiquetas** que reflejan diferentes aspectos
- Se distingue claramente entre "Cliente de Eventos" y "Alto Valor"

---

## 🏷️ SISTEMA DE ETIQUETAS

Cada cliente ahora tiene etiquetas en **6 categorías**:

### **1️⃣ FRECUENCIA** (¿Cuán seguido compra?)
- 🔄 **Recurrente**: 4+ compras al año (484 clientes)
- 📅 **Esporádico**: 1-3 compras al año (674 clientes)
- ⚡ **Puntual**: Compra única (1,699 clientes)

### **2️⃣ TIPO DE COMPRA** (¿Qué compra?)
- 🎉 **Cliente de Eventos**: >70% compras para eventos (939 clientes)
- 🌸 **Cliente Individual**: >70% compras personales (1,526 clientes)
- 🎭 **Cliente Mixto**: Mezcla de ambos (392 clientes)

### **3️⃣ VALOR** (¿Cuánto gasta por pedido?)
- 💎 **Alto Valor**: Ticket >$50,000 (2,419 clientes)
- 💰 **Valor Medio**: Ticket $20,000-$50,000 (389 clientes)
- 🪙 **Valor Estándar**: Ticket <$20,000 (49 clientes)

### **4️⃣ PAGO** (¿Cómo paga?)
- ✅ **Cumplidor**: Paga a tiempo 90%+ (2,813 clientes)
- ⚠️ **Con Retrasos**: Retrasos ocasionales (28 clientes)
- ❌ **Moroso**: Retrasos frecuentes (16 clientes)

### **5️⃣ CANAL** (¿Dónde compra?)
- 💬 **Cliente WhatsApp**: >70% por WhatsApp (1,807 clientes)
- 🛒 **Cliente Shopify**: >70% online (946 clientes)
- 🔀 **Multicanal**: Usa varios canales (165 clientes)

### **6️⃣ SEGMENTO** (¿Qué tipo de cliente es?)
- 👤 **Personal**: Compras personales (2,245 clientes)
- 🕊️ **Funerales**: Cliente de servicios fúnebres (551 clientes)
- 💍 **Novias**: Cliente de matrimonios (56 clientes)
- 🏢 **Corporativo**: Compras empresariales (8 clientes)

---

## 🎉 DETECCIÓN DE EVENTOS

### **Eventos Identificados: 3,283 pedidos**

**Distribución por tipo:**
1. 🎂 **Cumpleaños**: 1,559 pedidos (47%)
2. 🕊️ **Funeral**: 1,309 pedidos (40%)
3. 💐 **Aniversario**: 194 pedidos (6%)
4. 💍 **Matrimonio**: 85 pedidos (3%)
5. 👶 **Nacimiento**: 59 pedidos (2%)
6. 🎉 **Otro**: 59 pedidos (2%)
7. 🏢 **Corporativo**: 11 pedidos (<1%)
8. 🎓 **Graduación**: 6 pedidos (<1%)
9. 🎊 **Inauguración**: 1 pedido (<1%)

**Fuentes de datos:**
- `eventos_trello.csv`: 38 eventos explícitos
- `pedidos_trello_COMPLETO.csv`: 2,795 eventos detectados por patrones

---

## 📊 EJEMPLOS DE PERFILES

### **Perfil A: "VIP Real"**
```
Etiquetas:
🔄 Recurrente
🌸 Cliente Individual
💎 Alto Valor
✅ Cumplidor
💬 Cliente WhatsApp
👤 Personal
```
**Interpretación**: Cliente frecuente que compra flores de alta gama regularmente para uso personal. **Este sí es un VIP verdadero**.

### **Perfil B: "Cliente de Evento"**
```
Etiquetas:
⚡ Puntual
🎉 Cliente de Eventos
💎 Alto Valor
✅ Cumplidor
🛒 Cliente Shopify
🕊️ Funerales
```
**Interpretación**: Cliente que compró 1 vez para un funeral con gasto alto. **NO es VIP**, es un cliente de evento único.

### **Perfil C: "Novia VIP"**
```
Etiquetas:
📅 Esporádico
🎭 Cliente Mixto
💎 Alto Valor
✅ Cumplidor
🔀 Multicanal
💍 Novias
```
**Interpretación**: Novia que compró para su matrimonio y algunas flores adicionales. Alto valor pero no recurrente.

---

## 🛠️ ESTRUCTURA TÉCNICA

### **Tablas Creadas:**

#### **1. `etiquetas_cliente`**
```sql
CREATE TABLE etiquetas_cliente (
    id INTEGER PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE,
    categoria VARCHAR(50),
    descripcion TEXT,
    color VARCHAR(20),
    icono VARCHAR(20),
    activa BOOLEAN DEFAULT 1,
    orden INTEGER
);
```

#### **2. `cliente_etiquetas`** (Relación N:M)
```sql
CREATE TABLE cliente_etiquetas (
    id INTEGER PRIMARY KEY,
    cliente_id VARCHAR(10),
    etiqueta_id INTEGER,
    fecha_asignacion DATETIME,
    asignacion_automatica BOOLEAN DEFAULT 1,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (etiqueta_id) REFERENCES etiquetas_cliente(id),
    UNIQUE(cliente_id, etiqueta_id)
);
```

### **Campos Agregados a `pedidos`:**
- `es_evento` (BOOLEAN): TRUE si es pedido de evento
- `tipo_evento` (VARCHAR): Tipo específico (Matrimonio, Funeral, etc.)

---

## 🚀 SCRIPTS EJECUTADOS

### **1. Crear sistema de etiquetas**
```bash
python3 backend/scripts/crear_sistema_etiquetas.py
```
- ✅ Crea tabla `etiquetas_cliente`
- ✅ Crea tabla `cliente_etiquetas`
- ✅ Inserta 19 etiquetas predefinidas

### **2. Identificar eventos**
```bash
python3 backend/scripts/identificar_eventos.py
```
- ✅ Procesa `eventos_trello.csv`
- ✅ Analiza `pedidos_trello_COMPLETO.csv`
- ✅ Marca 3,283 eventos
- ✅ Asigna tipo a cada evento

### **3. Clasificar clientes**
```bash
python3 backend/scripts/clasificar_clientes.py
```
- ✅ Analiza 2,857 clientes
- ✅ Asigna 17,206 etiquetas
- ✅ Promedio: 6 etiquetas por cliente

---

## 📡 API ACTUALIZADA

### **Modelo Cliente:**
```python
cliente.to_dict()
# Ahora incluye:
{
    "id": "CLI001",
    "nombre": "María García",
    ...
    "etiquetas": [
        {
            "id": 1,
            "nombre": "Recurrente",
            "categoria": "Frecuencia",
            "color": "#10B981",
            "icono": "🔄"
        },
        {
            "id": 5,
            "nombre": "Cliente Individual",
            "categoria": "Tipo",
            "color": "#EC4899",
            "icono": "🌸"
        },
        ...
    ]
}
```

---

## 🎨 PRÓXIMOS PASOS (FRONTEND)

### **1. Actualizar ClientesPage.jsx**
- Mostrar las etiquetas como badges coloridos
- Permitir filtrar por cualquier etiqueta
- Dashboard con distribución por categoría

### **2. Crear página de análisis de segmentación**
- Gráficos por cada dimensión
- Cruce de etiquetas (ej: "Recurrente + Alto Valor")
- Identificar clientes VIP reales

### **3. Actualizar estadísticas**
- Reemplazar "VIP/Fiel/Nuevo/Ocasional" por etiquetas múltiples
- Mostrar Top 10 combinaciones de etiquetas
- Análisis de eventos vs individuales

---

## 📈 BENEFICIOS DEL NUEVO SISTEMA

✅ **Eliminación de sesgos**
- Ya no se confunde "gasto alto de evento" con "cliente valioso"

✅ **Segmentación precisa**
- 6 dimensiones vs 1 dimensión anterior
- Múltiples etiquetas por cliente vs 1 etiqueta

✅ **Análisis mejorado**
- Puedes cruzar etiquetas: "Recurrente + Alto Valor + Individual"
- Identificar verdaderos VIPs vs clientes puntuales

✅ **Personalización de marketing**
- Mensaje diferente para "Cliente de Eventos" vs "Cliente Individual"
- Ofertas específicas por segmento

✅ **Trazabilidad de eventos**
- 3,283 eventos identificados y categorizados
- Análisis por tipo de evento (Matrimonios, Funerales, etc.)

---

## 🎯 CONSULTAS SQL ÚTILES

### **Clientes VIP reales (Recurrente + Alto Valor + Individual)**
```sql
SELECT c.id, c.nombre, c.total_pedidos, c.total_gastado
FROM clientes c
WHERE c.id IN (
    SELECT ce1.cliente_id
    FROM cliente_etiquetas ce1
    JOIN etiquetas_cliente e1 ON e1.id = ce1.etiqueta_id
    WHERE e1.nombre = 'Recurrente'
      AND ce1.cliente_id IN (
          SELECT ce2.cliente_id
          FROM cliente_etiquetas ce2
          JOIN etiquetas_cliente e2 ON e2.id = ce2.etiqueta_id
          WHERE e2.nombre = 'Alto Valor'
            AND ce2.cliente_id IN (
                SELECT ce3.cliente_id
                FROM cliente_etiquetas ce3
                JOIN etiquetas_cliente e3 ON e3.id = ce3.etiqueta_id
                WHERE e3.nombre = 'Cliente Individual'
            )
      )
)
ORDER BY c.total_gastado DESC;
```

### **Clientes de eventos con alto gasto (potencial para fidelización)**
```sql
SELECT c.*, GROUP_CONCAT(e.icono || ' ' || e.nombre) as etiquetas
FROM clientes c
JOIN cliente_etiquetas ce ON ce.cliente_id = c.id
JOIN etiquetas_cliente e ON e.id = ce.etiqueta_id
WHERE c.id IN (
    SELECT cliente_id
    FROM cliente_etiquetas ce
    JOIN etiquetas_cliente e ON e.id = ce.etiqueta_id
    WHERE e.nombre IN ('Cliente de Eventos', 'Alto Valor')
)
GROUP BY c.id
HAVING c.total_pedidos = 1  -- Compraron solo 1 vez
ORDER BY c.total_gastado DESC;
```

---

## ✨ CONCLUSIÓN

Has pasado de un sistema de **1 etiqueta por cliente** a un sistema de **6+ etiquetas por cliente** en **6 dimensiones diferentes**, eliminando sesgos y permitiendo análisis mucho más profundos.

Los clientes ahora están categorizados de forma precisa y puedes identificar:
- 🏆 **VIPs verdaderos**: Recurrente + Alto Valor + Individual
- 🎉 **Clientes de eventos**: Para marketing específico
- 💍 **Novias**: Segmento especial
- 🕊️ **Funerales**: Segmento sensible
- 🏢 **Corporativos**: B2B

**Total: 2,857 clientes clasificados con 17,206 etiquetas asignadas** 🎯

---

**Archivos creados:**
- `backend/scripts/crear_sistema_etiquetas.py`
- `backend/scripts/clasificar_clientes.py`
- `backend/scripts/identificar_eventos.py`
- `backend/migrar_personalizaciones.py`
- `backend/models/cliente.py` (actualizado)

**Próximo paso:** Reiniciar el backend y crear la interfaz visual en el frontend.

