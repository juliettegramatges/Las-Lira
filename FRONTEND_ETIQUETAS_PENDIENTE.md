# 🎨 Frontend de Etiquetas - Implementación Pendiente

## ✅ YA IMPLEMENTADO (Backend + Frontend Parcial)

### Backend:
- ✅ Sistema de etiquetas completo (tablas, relaciones)
- ✅ 2,857 clientes clasificados con 17,206 etiquetas
- ✅ Endpoint `/api/clientes/etiquetas` - Obtener etiquetas disponibles
- ✅ Endpoint `/api/clientes?etiquetas=1,2,3` - Filtrar por etiquetas
- ✅ Modelo Cliente actualizado con método `obtener_etiquetas()`
- ✅ 3,283 eventos identificados y categorizados

### Frontend:
- ✅ Componente `EtiquetaCliente.jsx` creado con tooltips
- ✅ Estados agregados a `ClientesPage.jsx`:
  - `etiquetasDisponibles`
  - `etiquetasFiltro`
  - `categoriaEtiquetaVisible`
- ✅ Función `cargarEtiquetasDisponibles()`
- ✅ useEffect actualizado para cargar etiquetas y filtrar

---

## 🚀 PASOS PENDIENTES (Frontend)

### 1️⃣ Agregar Sección de Filtros por Etiquetas

En `ClientesPage.jsx`, después de la barra de búsqueda, agregar:

```jsx
{/* Filtros por Etiquetas */}
{Object.keys(etiquetasDisponibles).length > 0 && (
  <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 mb-6">
    <div className="flex items-center gap-2 mb-3">
      <Tag className="h-5 w-5 text-indigo-600" />
      <h3 className="text-sm font-bold text-gray-900 uppercase">
        Filtrar por Etiquetas
      </h3>
    </div>
    
    <div className="space-y-3">
      {Object.entries(etiquetasDisponibles).map(([categoria, etiquetas]) => (
        <div key={categoria}>
          <p className="text-xs font-semibold text-gray-500 uppercase mb-2">
            {categoria}
          </p>
          <div className="flex flex-wrap gap-2">
            {etiquetas.map((etiqueta) => (
              <button
                key={etiqueta.id}
                onClick={() => {
                  if (etiquetasFiltro.includes(etiqueta.id)) {
                    setEtiquetasFiltro(etiquetasFiltro.filter(id => id !== etiqueta.id))
                  } else {
                    setEtiquetasFiltro([...etiquetasFiltro, etiqueta.id])
                  }
                  setPaginaActual(1)
                }}
                className={`
                  px-3 py-1.5 rounded-full text-sm font-medium transition-all
                  ${etiquetasFiltro.includes(etiqueta.id) 
                    ? 'ring-2 ring-offset-2 shadow-md' 
                    : 'opacity-60 hover:opacity-100'
                  }
                `}
                style={{
                  backgroundColor: `${etiqueta.color}15`,
                  color: etiqueta.color,
                  border: `2px solid ${etiqueta.color}`,
                  ...(etiquetasFiltro.includes(etiqueta.id) && {
                    ringColor: etiqueta.color
                  })
                }}
              >
                {etiqueta.icono} {etiqueta.nombre}
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
    
    {/* Botón para limpiar filtros */}
    {etiquetasFiltro.length > 0 && (
      <div className="mt-3 pt-3 border-t border-gray-200">
        <button
          onClick={() => {
            setEtiquetasFiltro([])
            setPaginaActual(1)
          }}
          className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
        >
          🗑️ Limpiar filtros ({etiquetasFiltro.length})
        </button>
      </div>
    )}
  </div>
)}
```

---

### 2️⃣ Mostrar Etiquetas en el Modal de Cliente

En el modal de detalle de cliente (`clienteSeleccionado`), agregar una sección de etiquetas después de la información básica:

```jsx
{/* Sección de Etiquetas del Cliente */}
{clienteSeleccionado.etiquetas && clienteSeleccionado.etiquetas.length > 0 && (
  <div className="border-t border-gray-200 pt-6">
    <div className="flex items-center gap-2 mb-4">
      <Tag className="h-5 w-5 text-indigo-600" />
      <h4 className="text-sm font-bold text-gray-900 uppercase">
        Perfil del Cliente
      </h4>
    </div>
    
    <div className="space-y-3">
      {/* Agrupar etiquetas por categoría */}
      {Object.entries(
        clienteSeleccionado.etiquetas.reduce((acc, etiqueta) => {
          if (!acc[etiqueta.categoria]) acc[etiqueta.categoria] = []
          acc[etiqueta.categoria].push(etiqueta)
          return acc
        }, {})
      ).map(([categoria, etiquetas]) => (
        <div key={categoria}>
          <p className="text-xs font-semibold text-gray-500 uppercase mb-2">
            {categoria}
          </p>
          <div className="flex flex-wrap gap-2">
            {etiquetas.map((etiqueta) => (
              <EtiquetaCliente
                key={etiqueta.id}
                etiqueta={etiqueta}
                size="md"
                mostrarDescripcion={true}
              />
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
)}
```

---

### 3️⃣ Mostrar Etiquetas en las Cards de Clientes

En la tabla/lista de clientes, agregar una columna o sección para mostrar las etiquetas principales:

```jsx
{/* En cada fila/card de cliente */}
{cliente.etiquetas && cliente.etiquetas.length > 0 && (
  <div className="mt-2 flex flex-wrap gap-1">
    {cliente.etiquetas.slice(0, 3).map((etiqueta) => (
      <EtiquetaCliente
        key={etiqueta.id}
        etiqueta={etiqueta}
        size="sm"
        mostrarDescripcion={false}
      />
    ))}
    {cliente.etiquetas.length > 3 && (
      <span className="text-xs text-gray-500 italic">
        +{cliente.etiquetas.length - 3} más
      </span>
    )}
  </div>
)}
```

---

### 4️⃣ Actualizar Estadísticas para Incluir Etiquetas

Agregar una nueva sección de estadísticas por etiquetas:

```jsx
{/* Estadísticas por Etiquetas */}
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
  {Object.entries(etiquetasDisponibles).slice(0, 3).map(([categoria, etiquetas]) => (
    <div key={categoria} className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
      <h4 className="text-sm font-bold text-gray-900 mb-3">{categoria}</h4>
      <div className="space-y-2">
        {etiquetas.slice(0, 3).map((etiqueta) => {
          const count = clientes.filter(c => 
            c.etiquetas?.some(e => e.id === etiqueta.id)
          ).length
          return (
            <div key={etiqueta.id} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span>{etiqueta.icono}</span>
                <span className="text-sm text-gray-700">{etiqueta.nombre}</span>
              </div>
              <span className="text-sm font-bold text-gray-900">{count}</span>
            </div>
          )
        })}
      </div>
    </div>
  ))}
</div>
```

---

## 🎯 RESULTADO FINAL ESPERADO

Después de implementar estos cambios, tendrás:

1. **Filtros dinámicos** por etiquetas con botones coloridos
2. **Modal de cliente mejorado** mostrando todas sus etiquetas con tooltips descriptivos
3. **Vista rápida** de etiquetas en cada card de cliente
4. **Estadísticas** por etiquetas más relevantes
5. **Sistema completo** que distingue entre:
   - 🏆 VIPs verdaderos (Recurrente + Alto Valor + Individual)
   - 🎉 Clientes de Eventos (no confundidos con VIPs)
   - 💍 Novias, 🕊️ Funerales, 🏢 Corporativos, etc.

---

## 🚀 CÓMO PROBAR

1. **Reiniciar el backend**:
```bash
cd /Users/juliettegramatges/Las-Lira/backend
python3 app.py
```

2. **Iniciar el frontend**:
```bash
cd /Users/juliettegramatges/Las-Lira/frontend
npm run dev
```

3. **Verificar endpoints**:
- `GET http://localhost:5001/api/clientes/etiquetas` → Debe devolver etiquetas agrupadas
- `GET http://localhost:5001/api/clientes?etiquetas=1,2` → Debe filtrar por etiquetas
- `GET http://localhost:5001/api/clientes/CLI001` → Cliente debe incluir `etiquetas: [...]`

4. **Probar en el frontend**:
- Ir a Clientes
- Ver filtros de etiquetas aparecen
- Seleccionar etiquetas para filtrar
- Abrir modal de cliente y ver etiquetas con tooltips

---

## 📝 NOTAS IMPORTANTES

- Las etiquetas se cargan automáticamente al iniciar
- Los filtros son acumulativos (AND logic)
- Los tooltips muestran la descripción completa
- Los colores e iconos son configurables por etiqueta
- El sistema es escalable: se pueden agregar más etiquetas fácilmente

---

¡El backend está 100% listo! Solo falta completar estos 4 pasos en el frontend. 🚀

