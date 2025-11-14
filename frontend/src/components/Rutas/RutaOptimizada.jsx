import { useState, useEffect, useRef } from 'react'
import { MapPin, Clock, Navigation, TrendingUp, AlertCircle, Loader2, Package, Phone, User } from 'lucide-react'

/**
 * Componente para visualizar ruta optimizada en Google Maps
 */
function RutaOptimizada({ rutaData }) {
  const [mapaListo, setMapaListo] = useState(false)
  const [googleMapsLoaded, setGoogleMapsLoaded] = useState(false)
  const [errorCarga, setErrorCarga] = useState(null)
  const mapContainerRef = useRef(null)
  const mapRef = useRef(null)
  const markersRef = useRef([])
  const directionsRendererRef = useRef(null)

  // Cargar Google Maps API si no está disponible
  useEffect(() => {
    // Verificar si ya está cargado
    if (window.google && window.google.maps) {
      setGoogleMapsLoaded(true)
      return
    }

    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY
    if (!apiKey) {
      setErrorCarga('API Key de Google Maps no configurada')
      return
    }

    // Verificar si el script ya está en el DOM
    const existingScript = document.querySelector(`script[src*="maps.googleapis.com"]`)
    if (existingScript) {
      // Esperar a que se cargue
      const checkLoaded = setInterval(() => {
        if (window.google && window.google.maps) {
          setGoogleMapsLoaded(true)
          clearInterval(checkLoaded)
        }
      }, 100)
      return () => clearInterval(checkLoaded)
    }

    // Cargar el script de Google Maps
    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places,geometry&language=es&region=CL&loading=async`
    script.async = true
    script.defer = true
    script.onload = () => {
      if (window.google && window.google.maps) {
        setGoogleMapsLoaded(true)
      }
    }
    script.onerror = () => {
      setErrorCarga('Error al cargar Google Maps. Verifica tu API Key y que esté autorizada para localhost:3001')
    }

    document.head.appendChild(script)

    return () => {
      // No remover el script para evitar problemas de recarga
    }
  }, [])

  // Inicializar mapa cuando Google Maps esté cargado y haya datos
  useEffect(() => {
    if (!rutaData || !googleMapsLoaded) return

    // Esperar a que el contenedor esté en el DOM y sea visible
    const checkAndInit = () => {
      if (!mapContainerRef.current) {
        // Si el contenedor aún no existe, esperar un poco más
        setTimeout(checkAndInit, 50)
        return
      }

      // Verificar que el contenedor tenga dimensiones
      const rect = mapContainerRef.current.getBoundingClientRect()
      if (rect.width === 0 || rect.height === 0) {
        // Si no tiene dimensiones, esperar un poco más
        setTimeout(checkAndInit, 50)
        return
      }

      // Ahora sí inicializar el mapa
      initMap()
    }

    // Pequeño delay inicial para asegurar que el DOM esté listo
    const timer = setTimeout(checkAndInit, 100)

    return () => clearTimeout(timer)
  }, [rutaData, googleMapsLoaded])

  const initMap = () => {
    try {
      if (!mapContainerRef.current || !window.google || !window.google.maps) {
        console.error('No se puede inicializar el mapa: contenedor o Google Maps no disponible')
        return
      }

      // Verificar que el contenedor esté en el DOM y tenga dimensiones
      const rect = mapContainerRef.current.getBoundingClientRect()
      if (rect.width === 0 || rect.height === 0) {
        console.warn('El contenedor del mapa no tiene dimensiones, reintentando...')
        setTimeout(() => initMap(), 100)
        return
      }

      // Limpiar mapa anterior si existe
      if (mapRef.current) {
        markersRef.current.forEach(marker => marker.setMap(null))
        markersRef.current = []
        mapRef.current = null
      }

      const puntoInicio = rutaData.punto_inicio

      // Crear mapa
      const map = new window.google.maps.Map(mapContainerRef.current, {
      center: { lat: puntoInicio.latitud, lng: puntoInicio.longitud },
      zoom: 12,
      mapTypeControl: false,
      streetViewControl: false,
    })

    mapRef.current = map
    markersRef.current = [] // Inicializar array de markers

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

    // Dibujar ruta si usamos Google Directions API con polyline
    if (rutaData.metodo === 'google_directions' && rutaData.polyline) {
      try {
        // Decodificar polyline de Google y dibujarla
        const path = window.google.maps.geometry.encoding.decodePath(rutaData.polyline)

        const routePath = new window.google.maps.Polyline({
          path: path,
          geodesic: true,
          strokeColor: '#4285F4',
          strokeOpacity: 0.8,
          strokeWeight: 5,
          map: map
        })

        // Ajustar zoom para mostrar toda la ruta
        const bounds = new window.google.maps.LatLngBounds()
        bounds.extend({ lat: puntoInicio.latitud, lng: puntoInicio.longitud })

        rutaData.ruta_optimizada.forEach(parada => {
          bounds.extend({ lat: parada.latitud, lng: parada.longitud })
        })

        map.fitBounds(bounds)
      } catch (error) {
        console.error('Error al decodificar polyline:', error)
        // Fallback a líneas simples
        dibujarLineaSimple(map, puntoInicio, rutaData.ruta_optimizada)
      }
    } else {
      // Dibujar líneas simples entre puntos
      dibujarLineaSimple(map, puntoInicio, rutaData.ruta_optimizada)
    }

    setMapaListo(true)
    } catch (error) {
      console.error('Error al inicializar el mapa:', error)
      setErrorCarga(`Error al inicializar el mapa: ${error.message}`)
    }
  }

  const dibujarLineaSimple = (map, puntoInicio, rutaOptimizada) => {
    const lineCoordinates = [
      { lat: puntoInicio.latitud, lng: puntoInicio.longitud },
      ...rutaOptimizada.map(p => ({ lat: p.latitud, lng: p.longitud }))
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

  const abrirEnGoogleMaps = () => {
    if (rutaData && rutaData.google_maps_url) {
      window.open(rutaData.google_maps_url, '_blank')
    }
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
          <div className="mt-4 space-y-2">
            <a
              href={rutaData.google_maps_url}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold py-4 px-6 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200"
            >
              <div className="flex items-center justify-center gap-3">
                <Navigation className="h-7 w-7" />
                <div className="text-left">
                  <div className="text-lg">Abrir Navegación en Google Maps</div>
                  <div className="text-xs opacity-90 font-normal">Ruta en auto con todos los puntos de entrega</div>
                </div>
              </div>
            </a>
            <p className="text-xs text-center text-gray-600">
              🚗 Se abrirá Google Maps con la ruta optimizada lista para navegar
            </p>
          </div>
        )}
      </div>

      {/* Mapa */}
      <div className="bg-white rounded-lg overflow-hidden shadow-lg border border-gray-200">
        {errorCarga ? (
          <div className="p-8 text-center">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-3" />
            <p className="text-red-600 font-semibold">{errorCarga}</p>
            <div className="text-sm text-gray-600 mt-4 max-w-2xl mx-auto text-left">
              <p className="font-semibold mb-2">Para solucionar el error "RefererNotAllowedMapError":</p>
              <ol className="list-decimal list-inside space-y-2">
                <li>Ve a <a href="https://console.cloud.google.com/apis/credentials" target="_blank" rel="noopener noreferrer" className="text-blue-600 underline hover:text-blue-800">Google Cloud Console → Credenciales</a></li>
                <li>Haz clic en tu API Key para editarla</li>
                <li>En <strong>"Restricciones de aplicación"</strong>, selecciona <strong>"Referentes HTTP (sitios web)"</strong></li>
                <li>Agrega estos referentes:
                  <ul className="list-disc list-inside ml-6 mt-1 space-y-1">
                    <li><code className="bg-gray-100 px-1 rounded">http://localhost:3001/*</code></li>
                    <li><code className="bg-gray-100 px-1 rounded">http://127.0.0.1:3001/*</code></li>
                    <li><code className="bg-gray-100 px-1 rounded">http://localhost:*/*</code></li>
                  </ul>
                </li>
                <li>Haz clic en <strong>"Guardar"</strong> y espera 1-2 minutos</li>
              </ol>
            </div>
          </div>
        ) : !googleMapsLoaded ? (
          <div className="p-8 text-center">
            <Loader2 className="h-12 w-12 text-blue-500 mx-auto mb-3 animate-spin" />
            <p className="text-gray-600">Cargando Google Maps...</p>
          </div>
        ) : (
          <div
            ref={mapContainerRef}
            className="w-full h-96"
            style={{ minHeight: '384px' }}
          />
        )}
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

                  <div className="flex items-center gap-4 mt-2 flex-wrap">
                    {parada.hora_llegada_estimada && (
                      <div className={`flex items-center gap-2 text-sm font-bold px-3 py-1 rounded ${
                        parada.llegara_tarde
                          ? 'text-red-700 bg-red-50 border border-red-200'
                          : 'text-purple-700 bg-purple-50'
                      }`}>
                        <Clock className="h-4 w-4" />
                        Llegada estimada: {parada.hora_llegada_estimada}
                        {parada.llegara_tarde && (
                          <AlertCircle className="h-4 w-4 ml-1" />
                        )}
                      </div>
                    )}
                    {parada.hora_entrega && (
                      <div className="flex items-center gap-2 text-sm text-blue-600 font-medium">
                        <Clock className="h-4 w-4" />
                        Hora solicitada: {parada.hora_entrega}
                      </div>
                    )}
                  </div>
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
