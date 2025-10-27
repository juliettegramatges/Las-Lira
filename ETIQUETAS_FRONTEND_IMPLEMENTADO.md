# Sistema de Etiquetas - Frontend Implementado

## ✅ Funcionalidades Implementadas

### 1. **Filtros por Etiquetas**
Ubicación: Arriba de la tabla de clientes, después de la barra de búsqueda.

**Características:**
- Muestra todas las etiquetas disponibles agrupadas por categoría (Frecuencia, Tipo, Valor, Pago, Canal, Segmento)
- Filtros interactivos: al hacer clic en una etiqueta, se filtra la lista de clientes
- Contador de filtros activos
- Botón "Limpiar filtros" para resetear todos los filtros
- Estilos dinámicos: las etiquetas seleccionadas se resaltan con un ring
- Colores e iconos personalizados por etiqueta

**Cómo funciona:**
- El componente carga todas las etiquetas disponibles desde `/api/clientes/etiquetas`
- Al seleccionar una etiqueta, se agrega su ID a `etiquetasFiltro`
- La petición a `/api/clientes` incluye las etiquetas seleccionadas como parámetro
- El backend filtra los clientes que tienen al menos una de las etiquetas seleccionadas

### 2. **Etiquetas en la Tabla de Clientes**
Ubicación: Nueva columna "Etiquetas" en la tabla principal de clientes.

**Características:**
- Muestra hasta 3 etiquetas por cliente
- Si hay más de 3, muestra un contador "+N"
- Usa el componente `EtiquetaCliente` para renderizar cada etiqueta
- Tooltips informativos al pasar el mouse sobre cada etiqueta
- Mensaje "Sin etiquetas" si el cliente no tiene ninguna

**Diseño:**
- Etiquetas compactas con iconos
- Colores personalizados según el tipo de etiqueta
- Responsive: se adapta al ancho de la columna

### 3. **Etiquetas en el Modal de Detalle**
Ubicación: Modal que se abre al hacer clic en un cliente, entre "Información de Contacto" y "Notas".

**Características:**
- Sección dedicada "Etiquetas" con icono de Tag
- Etiquetas agrupadas por categoría
- Muestra todas las etiquetas del cliente (sin límite)
- Tooltips con descripción completa de cada etiqueta
- Diseño consistente con el resto del modal

**Información en Tooltips:**
- Icono y nombre de la etiqueta
- Descripción detallada
- Categoría a la que pertenece
- Colores personalizados por etiqueta

### 4. **Componente `EtiquetaCliente`**
Ubicación: `frontend/src/components/EtiquetaCliente.jsx`

**Props:**
- `etiqueta`: Objeto con la información de la etiqueta (obligatorio)
- `mostrarDescripcion`: Boolean para mostrar/ocultar tooltip (default: true)
- `size`: Tamaño de la etiqueta - 'sm', 'md', 'lg' (default: 'md')

**Características:**
- Tooltips con descripción completa
- Estilos dinámicos basados en el color de la etiqueta
- Animaciones suaves en hover
- z-index alto para evitar que se corten los tooltips

## 🎨 Paleta de Colores de Etiquetas

El backend ya incluye colores predefinidos para cada etiqueta:

### Frecuencia
- 🔥 **Habitual**: `#EF4444` (rojo)
- ⭐ **Recurrente**: `#F59E0B` (naranja)
- 🆕 **Nuevo**: `#10B981` (verde)
- 🌙 **Ocasional**: `#6B7280` (gris)

### Tipo
- 💐 **Flores Individuales**: `#EC4899` (rosa)
- 🎁 **Regalos Corporativos**: `#8B5CF6` (morado)
- 🎉 **Eventos**: `#F97316` (naranja)

### Valor
- 💎 **VIP**: `#A855F7` (morado)
- 💰 **Alto Valor**: `#3B82F6` (azul)
- 📊 **Valor Medio**: `#10B981` (verde)
- 💵 **Bajo Valor**: `#6B7280` (gris)

### Pago
- ✅ **Cumplidor**: `#10B981` (verde)
- ⚠️ **Pago Tardío**: `#F59E0B` (naranja)
- ❌ **Incumplidor**: `#EF4444` (rojo)

### Canal
- 📱 **WhatsApp**: `#10B981` (verde)
- 🌐 **Shopify**: `#8B5CF6` (morado)
- 📧 **Email**: `#3B82F6` (azul)
- 📞 **Teléfono**: `#6B7280` (gris)

### Segmento
- 🏢 **B2B**: `#8B5CF6` (morado)
- 👤 **B2C**: `#EC4899` (rosa)
- 🎯 **Premium**: `#F59E0B` (naranja)
- 👥 **Masivo**: `#6B7280` (gris)

## 🔄 Flujo de Datos

1. **Carga inicial:**
   - `cargarEtiquetasDisponibles()` obtiene todas las etiquetas desde `/api/clientes/etiquetas`
   - Se guardan en `etiquetasDisponibles` agrupadas por categoría

2. **Filtrado:**
   - Usuario selecciona etiquetas desde la sección de filtros
   - Se actualizan `etiquetasFiltro` (array de IDs)
   - `cargarClientes()` envía las etiquetas como parámetro query
   - Backend filtra y devuelve solo clientes con esas etiquetas

3. **Visualización:**
   - Cada cliente en la respuesta incluye su array de `etiquetas`
   - La tabla muestra hasta 3 etiquetas con el componente `EtiquetaCliente`
   - El modal de detalle muestra todas las etiquetas agrupadas por categoría

## 📝 Estados del Componente

```javascript
// Estados para etiquetas
const [etiquetasDisponibles, setEtiquetasDisponibles] = useState({})
const [etiquetasFiltro, setEtiquetasFiltro] = useState([])
const [categoriaEtiquetaVisible, setCategoriaEtiquetaVisible] = useState(null)
```

## 🔍 Funciones Clave

### `cargarEtiquetasDisponibles()`
Carga todas las etiquetas disponibles desde el backend.

```javascript
const cargarEtiquetasDisponibles = async () => {
  try {
    const response = await axios.get(`${API_URL}/clientes/etiquetas`)
    setEtiquetasDisponibles(response.data)
  } catch (error) {
    console.error('Error al cargar etiquetas:', error)
  }
}
```

### `cargarClientes()` - Modificada
Ahora incluye las etiquetas seleccionadas en la petición.

```javascript
// Se construye el parámetro etiquetas
if (etiquetasFiltro.length > 0) {
  params.etiquetas = etiquetasFiltro.join(',')
}
```

## ✨ Mejoras Visuales

- **Tooltips elegantes:** Con flecha, colores personalizados y animaciones
- **Filtros interactivos:** Feedback visual al seleccionar/deseleccionar
- **Consistencia:** Mismo diseño de etiquetas en tabla y modal
- **Responsivo:** Se adapta a diferentes tamaños de pantalla

## 🚀 Próximos Pasos Opcionales

1. **Edición de etiquetas:** Permitir agregar/quitar etiquetas desde el modal de cliente
2. **Estadísticas por etiqueta:** Mostrar métricas globales por tipo de etiqueta
3. **Exportación:** Incluir etiquetas en la exportación a Excel
4. **Búsqueda:** Permitir buscar clientes por nombre de etiqueta

## 🧪 Para Probar

1. Abre http://localhost:3001
2. Ve a la página de "Clientes"
3. Verifica que aparezca la sección de "Filtrar por Etiquetas"
4. Haz clic en algunas etiquetas para filtrar
5. Verifica que la tabla muestre las etiquetas en cada fila
6. Haz clic en un cliente para ver su detalle
7. Verifica que aparezca la sección "Etiquetas" en el modal
8. Pasa el mouse sobre una etiqueta para ver su tooltip con descripción

## 📌 Archivos Modificados

- `frontend/src/pages/ClientesPage.jsx` - Componente principal con filtros y visualización
- `frontend/src/components/EtiquetaCliente.jsx` - Componente reutilizable para etiquetas

## 🔗 Endpoints Backend Utilizados

- `GET /api/clientes/etiquetas` - Lista todas las etiquetas disponibles
- `GET /api/clientes?etiquetas=1,2,3` - Lista clientes filtrados por etiquetas
- `GET /api/clientes/<id>` - Detalle del cliente (incluye sus etiquetas)

---

✅ **Todo implementado y listo para usar!**

