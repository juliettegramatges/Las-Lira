import { useState, useEffect, useRef } from 'react'
import { MapPin, Clock, Navigation, TrendingUp, AlertCircle, Loader2, Package, Phone, User } from 'lucide-react'

/**
 * Componente para visualizar ruta optimizada en Google Maps
 */
function RutaOptimizada({ rutaData }) {
  const [mapaListo, setMapaListo] = useState(false)
  const mapContainerRef = useRef(null)
  const mapRef = useRef(null)
  const markersRef = useRef([])
  const directionsRendererRef = useRef(null)

  useEffect(() => {
    if (!rutaData || !window.google || !window.google.maps) return

    initMap()
  }, [rutaData])

  const initMap = () => {
    if (!mapContainerRef.current) return

    const puntoInicio = rutaData.punto_inicio

    // Crear mapa
    const map = new window.google.maps.Map(mapContainerRef.current, {
      center: { lat: puntoInicio.latitud, lng: puntoInicio.longitud },
      zoom: 12,
      mapTypeControl: false,
      streetViewControl: false,
    })

    mapRef.current = map

    // Limpiar markers anteriores
    markersRef.current.forEach(marker => marker.setMap(null))
    markersRef.current = []

    // Marcador de inicio (tienda)
    const markerInicio = new window.google.maps.Marker({
      position: { lat: puntoInicio.latitud, lng: puntoInicio.longitud },
      map: map,
      title: 'Las Lira - Punto de Inicio',
      icon: {
        url: 'http://maps.google.com/mapfiles/ms/icons/green-dot.png'
      },
      label: {
        text: '🏠',
        fontSize: '18px'
      }
    })

    markersRef.current.push(markerInicio)

    // Marcadores para cada pedido
    rutaData.ruta_optimizada.forEach((parada, idx) => {
      const marker = new window.google.maps.Marker({
        position: { lat: parada.latitud, lng: parada.longitud },
        map: map,
        title: `${parada.orden}. ${parada.cliente}`,
        label: {
          text: String(parada.orden),
          color: 'white',
          fontWeight: 'bold'
        },
        icon: {
          url: parada.es_urgente
            ? 'http://maps.google.com/mapfiles/ms/icons/red-dot.png'
            : 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png'
        }
      })

      // Info window al hacer click
      const infoWindow = new window.google.maps.InfoWindow({
        content: `
          <div style="padding: 8px;">
            <strong style="font-size: 16px;">Parada ${parada.orden}</strong>
            <p style="margin: 4px 0;"><strong>Cliente:</strong> ${parada.cliente}</p>
            <p style="margin: 4px 0;"><strong>Dirección:</strong> ${parada.direccion}</p>
            <p style="margin: 4px 0;"><strong>Comuna:</strong> ${parada.comuna}</p>
            <p style="margin: 4px 0;"><strong>Teléfono:</strong> ${parada.telefono}</p>
            ${parada.hora_entrega ? `<p style="margin: 4px 0;"><strong>Hora entrega:</strong> ${parada.hora_entrega}</p>` : ''}
            ${parada.es_urgente ? '<p style="margin: 4px 0; color: red;"><strong>⚠️ URGENTE</strong></p>' : ''}
          </div>
        `
      })

      marker.addListener('click', () => {
        infoWindow.open(map, marker)
      })

      markersRef.current.push(marker)
    })

    // Dibujar ruta si usamos Google Directions API
    if (rutaData.metodo === 'google_directions' && rutaData.polyline) {
      if (directionsRendererRef.current) {
        directionsRendererRef.current.setMap(null)
      }

      const directionsRenderer = new window.google.maps.DirectionsRenderer({
        map: map,
        suppressMarkers: true, // Usar nuestros markers personalizados
        polylineOptions: {
          strokeColor: '#4285F4',
          strokeWeight: 5,
          strokeOpacity: 0.7
        }
      })

      directionsRendererRef.current = directionsRenderer

      // Decodificar polyline (si está disponible)
      const path = window.google.maps.geometry.encoding.decodePath(rutaData.polyline)

      const bounds = new window.google.maps.LatLngBounds()
      bounds.extend({ lat: puntoInicio.latitud, lng: puntoInicio.longitud })

      rutaData.ruta_optimizada.forEach(parada => {
        bounds.extend({ lat: parada.latitud, lng: parada.longitud })
      })

      map.fitBounds(bounds)
    } else {
      // Dibujar líneas simples entre puntos
      const lineCoordinates = [
        { lat: puntoInicio.latitud, lng: puntoInicio.longitud },
        ...rutaData.ruta_optimizada.map(p => ({ lat: p.latitud, lng: p.longitud }))
      ]

      const routePath = new window.google.maps.Polyline({
        path: lineCoordinates,
        geodesic: true,
        strokeColor: '#4285F4',
        strokeOpacity: 0.7,
        strokeWeight: 4,
        map: map
      })

      // Ajustar zoom para mostrar toda la ruta
      const bounds = new window.google.maps.LatLngBounds()
      lineCoordinates.forEach(coord => bounds.extend(coord))
      map.fitBounds(bounds)
    }

    setMapaListo(true)
  }

  if (!rutaData) {
    return (
      <div className="p-8 text-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
        <Navigation className="h-12 w-12 text-gray-400 mx-auto mb-3" />
        <p className="text-gray-600">Selecciona pedidos y optimiza la ruta para visualizarla aquí</p>
      </div>
    )
  }

  const metodoDescripcion = {
    'google_directions': '🗺️ Google Maps Directions API',
    'simple': '📍 Algoritmo de vecino más cercano',
    'simple_fallback': '📍 Algoritmo simple (fallback)',
    'unico': '📦 Ruta con un solo pedido'
  }

  return (
    <div className="space-y-4">
      {/* Resumen de la ruta */}
      <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg p-4 border border-blue-200">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-bold text-blue-900 flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Ruta Optimizada
          </h3>
          <span className="text-xs bg-white px-3 py-1 rounded-full text-blue-700 font-medium">
            {metodoDescripcion[rutaData.metodo] || rutaData.metodo}
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="bg-white rounded-lg p-3 shadow-sm">
            <p className="text-xs text-gray-500 mb-1">Paradas</p>
            <p className="text-2xl font-bold text-blue-600">{rutaData.ruta_optimizada.length}</p>
          </div>

          {rutaData.distancia_total_km !== undefined && (
            <div className="bg-white rounded-lg p-3 shadow-sm">
              <p className="text-xs text-gray-500 mb-1">Distancia Total</p>
              <p className="text-2xl font-bold text-green-600">{rutaData.distancia_total_km} km</p>
            </div>
          )}

          {rutaData.tiempo_total_min !== undefined && (
            <div className="bg-white rounded-lg p-3 shadow-sm">
              <p className="text-xs text-gray-500 mb-1">Tiempo Estimado</p>
              <p className="text-2xl font-bold text-orange-600">{Math.floor(rutaData.tiempo_total_min)} min</p>
            </div>
          )}

          {rutaData.hora_inicio && (
            <div className="bg-white rounded-lg p-3 shadow-sm">
              <p className="text-xs text-gray-500 mb-1">Hora Inicio</p>
              <p className="text-2xl font-bold text-purple-600">{rutaData.hora_inicio}</p>
            </div>
          )}
        </div>

        <div className="mt-3 p-2 bg-white rounded flex items-center gap-2 text-sm">
          <MapPin className="h-4 w-4 text-green-600" />
          <span className="font-medium">Inicio:</span>
          <span className="text-gray-700">{rutaData.punto_inicio.direccion}</span>
        </div>

        {/* Botón para abrir en Google Maps */}
        {rutaData.google_maps_url && (
          <div className="mt-3">
            <a
              href={rutaData.google_maps_url}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold py-3 px-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center gap-3 text-lg"
            >
              <Navigation className="h-6 w-6" />
              Abrir Ruta en Google Maps
              <span className="text-sm opacity-90">(Navegación)</span>
            </a>
            <p className="text-xs text-center text-gray-600 mt-2">
              Se abrirá la ruta completa con todos los puntos de entrega en orden
            </p>
          </div>
        )}
      </div>

      {/* Mapa */}
      <div className="bg-white rounded-lg overflow-hidden shadow-lg border border-gray-200">
        <div
          ref={mapContainerRef}
          className="w-full h-96"
        />
      </div>

      {/* Lista de paradas */}
      <div className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
        <div className="bg-gray-50 border-b border-gray-200 px-4 py-3">
          <h4 className="font-bold text-gray-900 flex items-center gap-2">
            <Package className="h-5 w-5 text-blue-600" />
            Secuencia de Entregas
          </h4>
        </div>
        <div className="divide-y divide-gray-200">
          {rutaData.ruta_optimizada.map((parada, idx) => (
            <div
              key={idx}
              className={`p-4 hover:bg-gray-50 transition-colors ${
                parada.es_urgente ? 'bg-red-50 border-l-4 border-red-500' : ''
              }`}
            >
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-bold text-lg ${
                    parada.es_urgente ? 'bg-red-500' : 'bg-blue-500'
                  }`}>
                    {parada.orden}
                  </div>
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h5 className="font-bold text-gray-900">{parada.cliente}</h5>
                    {parada.es_urgente && (
                      <span className="bg-red-100 text-red-700 px-2 py-0.5 rounded text-xs font-semibold">
                        URGENTE
                      </span>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm text-gray-600 mt-2">
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-gray-400 flex-shrink-0" />
                      <span className="truncate">{parada.direccion}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Phone className="h-4 w-4 text-gray-400 flex-shrink-0" />
                      <span>{parada.telefono}</span>
                    </div>
                  </div>

                  {parada.hora_entrega && (
                    <div className="flex items-center gap-2 text-sm text-blue-600 font-medium mt-2">
                      <Clock className="h-4 w-4" />
                      Hora de entrega solicitada: {parada.hora_entrega}
                    </div>
                  )}
                </div>

                <div className="flex-shrink-0 text-right">
                  {parada.distancia_desde_anterior_km !== undefined && (
                    <div className="text-sm mb-1">
                      <span className="text-gray-500">Distancia:</span>
                      <span className="ml-1 font-semibold text-green-600">
                        {parada.distancia_desde_anterior_km} km
                      </span>
                    </div>
                  )}
                  {parada.tiempo_desde_anterior_min !== undefined && (
                    <div className="text-sm">
                      <span className="text-gray-500">Tiempo:</span>
                      <span className="ml-1 font-semibold text-orange-600">
                        {parada.tiempo_desde_anterior_min} min
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default RutaOptimizada
