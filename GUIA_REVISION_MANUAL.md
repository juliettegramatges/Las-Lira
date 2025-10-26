# 📋 Guía de Revisión Manual - Pedidos CSV

## 🎯 Resumen de la Limpieza

Se procesaron **8,685 pedidos** del archivo Trello con las siguientes correcciones automáticas:

### ✅ Correcciones Realizadas

1. **6,543 teléfonos normalizados**
   - Removidos puntos y espacios inconsistentes
   - Formato estandarizado: `9731 4424` o `2224 2420`
   - Mantenidos números internacionales: `+34 605 22 40 21`

2. **737 nombres de clientes limpiados**
   - Removidos sufijos `1:2`, `2:2`, `3:3`, etc.
   - Ejemplo: `ISABEL BELAN 1:2` → `ISABEL BELAN`

3. **1 desfase de columnas corregido**
   - Separado teléfono de texto de producto

---

## ⚠️ Casos para Revisión Manual (373 casos)

El archivo `pedidos_revisar.csv` contiene casos donde el campo "celular" tiene:
- **Nombres de empresas** (ej: "Fagasi S.A.", "COPEC")
- **Nombres de personas** (ej: "GEORGE ANASTASSIOUS", "CONSTANZA")
- **Códigos especiales** (ej: "EEUU", "SIN NUMERO")

### 📝 Tipos de Casos Especiales

#### 1️⃣ Empresas en Campo Teléfono
```csv
Cliente: CARMEN GONZALEZ
Celular: Fagasi S.A.
```
**ACCIÓN SUGERIDA:** 
- Buscar el teléfono real de Carmen González
- Mover "Fagasi S.A." al campo de notas o crear campo "Empresa"

#### 2️⃣ Nombres de Contacto en Campo Teléfono
```csv
Cliente: ANGELICA MENENDEZ
Celular: Mackenna, Cruzat y Cia.
```
**ACCIÓN SUGERIDA:**
- Buscar teléfono de Angelica Menendez
- "Mackenna, Cruzat y Cia." puede ser la empresa relacionada

#### 3️⃣ Códigos Especiales
```csv
Cliente: TALAVERA
Celular: EEUU
```
**ACCIÓN SUGERIDA:**
- Cliente internacional, revisar si hay teléfono en el mensaje o dirección
- Buscar en pedidos anteriores del mismo cliente

#### 4️⃣ Sin Número
```csv
Cliente: PAULINA MAFFEI
Celular: SIN NUMERO
```
**ACCIÓN SUGERIDA:**
- Buscar en pedidos anteriores del mismo cliente
- Verificar si retira en local (RETIRA)

---

## 🔍 Cómo Revisar los Casos

### Paso 1: Abrir el archivo de revisión
```bash
open pedidos_revisar.csv
```

### Paso 2: Buscar el cliente en el archivo limpio
Para cada caso problemático, busca el mismo cliente en `pedidos_limpio.csv`:

```bash
grep "CARMEN GONZALEZ" pedidos_limpio.csv
```

Esto te mostrará todos los pedidos de ese cliente. Si tiene otros pedidos con teléfono válido, **úsalo para completar los registros faltantes**.

### Paso 3: Crear un Excel con correcciones
1. Abre `pedidos_revisar.csv` en Excel
2. Agrega una columna: `TELEFONO_CORRECTO`
3. Completa los teléfonos correctos investigando:
   - Otros pedidos del mismo cliente
   - Información en el campo "mensaje" o "direccion"
   - Contactos guardados en WhatsApp

---

## 📊 Casos Más Comunes

### Clientes Corporativos (20 casos)
- **CARMEN GONZALEZ** → Fagasi S.A.
- **PAMELA TEARE** → COPEC
- **BNR GESTIONES** → CONSTANZA, LISSET GUAMAN

**ACCIÓN:** Estos son clientes corporativos. El teléfono real está en otros pedidos.

### Clientes Internacionales (8 casos)
- Código "EEUU"
- Números con formato internacional ya corregidos: `+34`, `+44`

### Clientes Sin Teléfono (5 casos)
- "SIN NUMERO"
- Clientes que retiran en local

---

## ✅ Ejemplo de Corrección Manual

### ANTES (en pedidos_revisar.csv):
```csv
fecha,cliente,celular,producto,MOTIVO_ERROR
2025-06-09,CARMEN GONZALEZ,Fagasi S.A.,IRIS MILÁN,TELEFONO_CON_TEXTO
```

### Buscar en pedidos_limpio.csv:
```bash
grep "CARMEN GONZALEZ" pedidos_limpio.csv
```

### Resultado:
```csv
2024-03-15,CARMEN GONZALEZ,9825 4567,...
2024-04-20,CARMEN GONZALEZ,9825 4567,...
```

### CORRECCIÓN:
```csv
fecha,cliente,celular,producto,TELEFONO_CORRECTO
2025-06-09,CARMEN GONZALEZ,Fagasi S.A.,IRIS MILÁN,9825 4567
```

---

## 🚀 Siguientes Pasos

1. ✅ **Usa `pedidos_limpio.csv`** como archivo principal
   - 8,685 registros totalmente procesados
   - Teléfonos normalizados
   - Clientes sin sufijos

2. 📝 **Revisa `pedidos_revisar.csv`**
   - 373 casos especiales
   - Identifica teléfonos correctos
   - Completa manualmente

3. 🔄 **Combina las correcciones**
   - Actualiza `pedidos_limpio.csv` con los teléfonos correctos
   - Genera versión final: `pedidos_FINAL.csv`

4. 💾 **Respaldo**
   - Mantén `pedidos.csv` como backup original

---

## 🛠️ Script de Ayuda

Para buscar rápidamente teléfonos de un cliente:

```bash
# Buscar todos los pedidos de un cliente
grep -i "NOMBRE_CLIENTE" pedidos_limpio.csv | cut -d',' -f4,5

# Contar cuántos pedidos tiene cada cliente
cut -d',' -f4 pedidos_limpio.csv | sort | uniq -c | sort -rn | head -20
```

---

## 📞 Contacto para Dudas

Si encuentras casos que no puedas resolver, marca la fila con un color en Excel y continúa con los siguientes.

**¡Los teléfonos de clientes recurrentes son los más importantes de completar!**


