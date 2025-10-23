# Sistema de Rutas Óptimas 🚗📦

## Descripción General

El sistema de Rutas Óptimas permite agrupar y visualizar los pedidos por comuna de destino para optimizar las entregas y reducir costos de transporte. Cada comuna tiene un precio de envío estándar definido.

## ✨ Características

### 1. **Agrupación por Comuna**
- Los pedidos se agrupan automáticamente según la comuna de entrega
- Cada pedido tiene un campo `comuna` que se registra al momento de crear el pedido
- Las comunas están predefinidas con sus respectivos precios de envío

### 2. **Precios de Envío por Comuna**

Los precios están organizados en 8 rangos según la distancia y complejidad de acceso:

| Precio | Comunas |
|--------|---------|
| **$7,000** | Las Condes, Lo Barnechea bajo, Vitacura |
| **$9,000** | El Arrayán bajo |
| **$10,000** | Providencia |
| **$12,000** | Clínicas (Alemana, Las Condes, Los Andes), El Arrayán alto, Lo Barnechea Alto, Recoleta |
| **$15,000** | Conchalí, La Reina, Parque del Recuerdo, Santiago Centro, Ñuñoa |
| **$18,000** | Huechuraba, Independencia |
| **$20,000** | La Granja, Lo Espejo, Macul, Quilicura, Quinta Normal, San Joaquín |
| **$22,000** | Cerro Navia, Lo Prado |
| **$25,000** | Cerrillos, El Bosque, Estación Central, La Cisterna, La Florida, Peñalolén, Pudahuel, Renca/Carrascal, San Miguel, San Ramón |
| **$30,000** | Colina-Chicureo, La Pintana, Maipú, Padre Hurtado, Pedro Aguirre Cerda, Peñaflor, Puente Alto, San Bernardo, Talagante |
| **$35,000** | Pirque |

### 3. **Zonas Geográficas**

Las comunas están organizadas en zonas para facilitar la planificación:

- **Zona Alta**: Las Condes, Vitacura, Lo Barnechea, El Arrayán
- **Zona Centro**: Providencia, Ñuñoa, Santiago Centro, Recoleta, Independencia
- **Zona Oriente**: La Reina, Peñalolén, Macul, La Florida
- **Zona Sur**: San Miguel, La Granja, San Joaquín, La Cisterna, El Bosque, San Ramón, La Pintana, Puente Alto, San Bernardo, Pedro Aguirre Cerda
- **Zona Poniente**: Maipú, Cerrillos, Estación Central, Quinta Normal, Pudahuel, Lo Prado, Cerro Navia, Renca
- **Zona Norte**: Quilicura, Huechuraba, Conchalí, Colina, Chicureo
- **Zona Periférica**: Padre Hurtado, Peñaflor, Talagante, Pirque, Lo Espejo
- **Clínicas**: Clínica Alemana, Clínica Las Condes, Clínica Los Andes, Parque del Recuerdo

## 🖥️ Interfaz de Usuario

La página de **Rutas de Despacho** ofrece 3 vistas:

### Vista 1: "Hoy"
- Muestra solo los pedidos con entrega para el día actual
- Ideal para la planificación de entregas del día
- Lista simple con todas las comunas que tienen pedidos hoy

### Vista 2: "Esta Semana"
- Organiza pedidos por día de la semana
- Agrupa por fecha de entrega y luego por comuna
- Permite planificar entregas con anticipación
- Muestra la cantidad de pedidos por día

### Vista 3: "Todos los Pendientes"
- Muestra todos los pedidos pendientes de entrega
- Filtra solo pedidos en estados activos (no archivados ni cancelados)
- Agrupación completa por comuna
- Útil para ver panorama general de entregas

## 📊 Información Mostrada

Para cada comuna, la vista muestra:

1. **Nombre de la Comuna**: Con ícono de ubicación
2. **Precio de Envío**: Con código de colores según precio
   - Verde: $7,000 - $9,000
   - Azul: $10,000 - $15,000
   - Amarillo: $18,000 - $25,000
   - Rojo: $30,000 - $35,000
3. **Cantidad de Pedidos**: Total de pedidos para esa comuna
4. **Total de Envíos**: Suma total de los costos de envío
5. **Lista de Clientes**: Nombres y detalles de los primeros pedidos
6. **Arreglo Pedido**: Descripción de cada pedido
7. **Precios**: Precio total y desglose del envío

## 🔄 API Endpoints

El sistema expone los siguientes endpoints:

### `GET /api/rutas/optimizar`
Obtiene pedidos agrupados por comuna para optimizar rutas.

**Parámetros:**
- `fecha_desde` (opcional): Filtrar desde esta fecha
- `fecha_hasta` (opcional): Filtrar hasta esta fecha
- `solo_pendientes` (opcional, default: true): Solo pedidos activos

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "comuna": "Las Condes",
      "precio_envio": 7000,
      "zona": "Zona Alta",
      "pedidos": [...],
      "total_pedidos": 5,
      "total_envios": 35000
    }
  ],
  "total_comunas": 15,
  "total_pedidos": 45
}
```

### `GET /api/rutas/por-fecha`
Obtiene pedidos agrupados por fecha y comuna.

**Parámetros:**
- `dias` (opcional, default: 7): Número de días hacia adelante

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "fecha": "2025-10-24",
      "total_pedidos": 8,
      "comunas": [
        {
          "comuna": "Providencia",
          "precio_envio": 10000,
          "pedidos": [...]
        }
      ]
    }
  ],
  "total_dias": 7
}
```

### `GET /api/rutas/resumen-hoy`
Resumen rápido de entregas para hoy.

**Respuesta:**
```json
{
  "success": true,
  "fecha": "2025-10-24",
  "total_pedidos": 12,
  "data": [...]
}
```

### `GET /api/rutas/comunas`
Lista todas las comunas disponibles con sus precios y zonas.

## 📝 Cómo Usar el Sistema

### 1. Al Crear un Pedido
1. Registrar la dirección completa del cliente
2. **Seleccionar la comuna** de destino de una lista desplegable
3. El sistema asignará automáticamente el precio de envío correspondiente
4. Si la comuna no está en la lista, usar la opción "Otra" y registrar manualmente el precio

### 2. Planificación de Entregas Diarias
1. Ir a la sección **"Rutas de Despacho"**
2. Seleccionar vista **"Hoy"**
3. Ver todos los pedidos agrupados por comuna
4. Planificar la ruta visitando primero las comunas con más pedidos
5. Considerar agrupar comunas de la misma zona geográfica

### 3. Planificación Semanal
1. Seleccionar vista **"Esta Semana"**
2. Ver distribución de pedidos por día
3. Identificar días con alta concentración de entregas
4. Reorganizar entregas si es necesario para equilibrar la carga
5. Coordinar con el equipo de preparación

### 4. Optimización de Rutas
**Estrategia recomendada:**

1. **Agrupar por zona**: Realizar todas las entregas de una zona antes de pasar a otra
2. **Priorizar volumen**: Visitar primero las comunas con más pedidos
3. **Considerar horarios**: Respetar ventanas de entrega de clínicas y oficinas
4. **Minimizar distancias**: Usar apps de navegación para optimizar el orden de visitas

**Ejemplo de ruta optimizada:**
- Mañana: Zona Alta (Las Condes, Vitacura, Lo Barnechea) - 8 pedidos
- Mediodía: Zona Centro (Providencia, Ñuñoa) - 6 pedidos
- Tarde: Zona Oriente (La Reina, Peñalolén) - 4 pedidos

## 💡 Consejos y Mejores Prácticas

1. **Actualizar estado de pedidos**: Marcar pedidos como "Listo para Despacho" solo cuando estén realmente listos
2. **Verificar direcciones**: Confirmar que la comuna en el sistema coincida con la dirección real
3. **Comunicación con clientes**: Avisar con anticipación si hay retrasos en comunas lejanas
4. **Preparación anticipada**: Para comunas con entregas frecuentes (ej: Las Condes), preparar los pedidos con un día de anticipación
5. **Backup de rutas**: Guardar rutas exitosas como referencia para futuros días similares

## 🔧 Configuración Técnica

El archivo `backend/config/comunas.py` contiene:
- Diccionario `COMUNAS_PRECIOS`: Mapeo de comuna → precio
- Diccionario `ZONAS`: Agrupación de comunas por zona geográfica
- Función `obtener_precio_envio(comuna)`: Retorna el precio para una comuna
- Función `obtener_zona_comuna(comuna)`: Retorna la zona de una comuna
- Función `buscar_comuna_similar(texto)`: Encuentra comuna a partir de texto

Para agregar o modificar comunas/precios, editar este archivo.

## 📈 Métricas y Análisis

El sistema permite analizar:
- **Comunas más frecuentes**: Identificar dónde se concentran las ventas
- **Ingresos por envío**: Calcular ganancia neta de envíos
- **Distribución geográfica**: Evaluar cobertura del negocio
- **Optimización de costos**: Identificar oportunidades de negociación con couriers

---

**Nota**: Este sistema está diseñado para mejorar continuamente. Si descubres nuevas comunas o necesitas ajustar precios, actualiza el archivo de configuración y regenera los archivos demo.

