import { useState, useEffect, useRef } from 'react'
import { MapPin, Loader2, AlertCircle, Navigation } from 'lucide-react'

/**
 * Componente para seleccionar dirección usando Google Maps Autocomplete y Geocoding
 * @param {Object} props
 * @param {string} props.direccion - Dirección actual
 * @param {string} props.comuna - Comuna actual
 * @param {Function} props.onDireccionChange - Callback cuando cambia la dirección
 * @param {number} props.latitud - Latitud actual (opcional)
 * @param {number} props.longitud - Longitud actual (opcional)
 * @param {Function} props.onCoordenadasChange - Callback cuando cambian las coordenadas
 */
function DireccionConMapa({
  direccion,
  comuna,
  onDireccionChange,
  latitud,
  longitud,
  onCoordenadasChange
}) {
  const [googleMapsLoaded, setGoogleMapsLoaded] = useState(false)
  const [loadingGeocoding, setLoadingGeocoding] = useState(false)
  const [error, setError] = useState(null)
  const inputRef = useRef(null)
  const autocompleteRef = useRef(null)
  const mapRef = useRef(null)
  const markerRef = useRef(null)
  const mapContainerRef = useRef(null)

  // Cargar Google Maps API
  useEffect(() => {
    const apiKey = import.meta.env.VITE_GOOGLE_MAPS_API_KEY

    if (!apiKey) {
      setError('API Key de Google Maps no configurada')
      return
    }

    // Verificar si ya está cargado
    if (window.google && window.google.maps) {
      setGoogleMapsLoaded(true)
      return
    }

    // Cargar el script de Google Maps
    const script = document.createElement('script')
    script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&language=es&region=CL`
    script.async = true
    script.defer = true
    script.onload = () => setGoogleMapsLoaded(true)
    script.onerror = () => setError('Error al cargar Google Maps')

    document.head.appendChild(script)

    return () => {
      // No remover el script para evitar problemas de recarga
    }
  }, [])

  // Inicializar mapa cuando Google Maps esté cargado
  useEffect(() => {
    if (!googleMapsLoaded || !mapContainerRef.current) return

    // Coordenadas iniciales (Santiago, Chile o las coordenadas del pedido)
    const initialLat = latitud || -33.4372
    const initialLng = longitud || -70.6506

    // Crear mapa
    const map = new window.google.maps.Map(mapContainerRef.current, {
      center: { lat: initialLat, lng: initialLng },
      zoom: latitud && longitud ? 16 : 12,
      mapTypeControl: false,
      streetViewControl: false,
      fullscreenControl: false,
    })

    mapRef.current = map

    // Crear marcador
    const marker = new window.google.maps.Marker({
      map: map,
      position: { lat: initialLat, lng: initialLng },
      draggable: true,
      title: 'Ubicación de entrega'
    })

    markerRef.current = marker

    // Evento cuando se arrastra el marcador
    marker.addListener('dragend', () => {
      const position = marker.getPosition()
      const lat = position.lat()
      const lng = position.lng()

      if (onCoordenadasChange) {
        onCoordenadasChange(lat, lng)
      }

      // Geocodificación inversa para obtener la dirección
      reverseGeocode(lat, lng)
    })

  }, [googleMapsLoaded])

  // Inicializar Autocomplete
  useEffect(() => {
    if (!googleMapsLoaded || !inputRef.current) return

    const autocomplete = new window.google.maps.places.Autocomplete(inputRef.current, {
      componentRestrictions: { country: 'cl' }, // Restringir a Chile
      fields: ['formatted_address', 'geometry', 'address_components', 'name'],
      types: ['address'] // Solo direcciones
    })

    autocompleteRef.current = autocomplete

    // Evento cuando se selecciona una dirección
    autocomplete.addListener('place_changed', () => {
      const place = autocomplete.getPlace()

      if (!place.geometry || !place.geometry.location) {
        setError('No se pudo obtener la ubicación de esa dirección')
        return
      }

      const lat = place.geometry.location.lat()
      const lng = place.geometry.location.lng()

      // Extraer comuna de los componentes de dirección
      let comunaExtraida = ''
      if (place.address_components) {
        for (const component of place.address_components) {
          if (component.types.includes('locality') || component.types.includes('administrative_area_level_3')) {
            comunaExtraida = component.long_name
            break
          }
        }
      }

      // Actualizar mapa y marcador
      if (mapRef.current && markerRef.current) {
        mapRef.current.setCenter({ lat, lng })
        mapRef.current.setZoom(16)
        markerRef.current.setPosition({ lat, lng })
      }

      // Callback con la información
      if (onDireccionChange) {
        onDireccionChange(place.formatted_address || place.name, comunaExtraida)
      }

      if (onCoordenadasChange) {
        onCoordenadasChange(lat, lng)
      }

      setError(null)
    })

  }, [googleMapsLoaded])

  // Geocodificación inversa (de coordenadas a dirección)
  const reverseGeocode = async (lat, lng) => {
    if (!window.google || !window.google.maps) return

    setLoadingGeocoding(true)
    const geocoder = new window.google.maps.Geocoder()

    try {
      const response = await geocoder.geocode({ location: { lat, lng } })

      if (response.results[0]) {
        const place = response.results[0]

        // Extraer comuna
        let comunaExtraida = ''
        for (const component of place.address_components) {
          if (component.types.includes('locality') || component.types.includes('administrative_area_level_3')) {
            comunaExtraida = component.long_name
            break
          }
        }

        if (onDireccionChange) {
          onDireccionChange(place.formatted_address, comunaExtraida)
        }
      }
    } catch (error) {
      console.error('Error en geocodificación inversa:', error)
      setError('Error al obtener la dirección')
    } finally {
      setLoadingGeocoding(false)
    }
  }

  // Geocodificar dirección cuando se escribe manualmente
  const geocodeDireccion = async () => {
    if (!direccion || !window.google || !window.google.maps) return

    setLoadingGeocoding(true)
    setError(null)

    const geocoder = new window.google.maps.Geocoder()

    try {
      const response = await geocoder.geocode({
        address: direccion,
        componentRestrictions: { country: 'CL' }
      })

      if (response.results[0]) {
        const place = response.results[0]
        const lat = place.geometry.location.lat()
        const lng = place.geometry.location.lng()

        // Actualizar mapa y marcador
        if (mapRef.current && markerRef.current) {
          mapRef.current.setCenter({ lat, lng })
          mapRef.current.setZoom(16)
          markerRef.current.setPosition({ lat, lng })
        }

        if (onCoordenadasChange) {
          onCoordenadasChange(lat, lng)
        }

        // Extraer comuna
        let comunaExtraida = ''
        for (const component of place.address_components) {
          if (component.types.includes('locality') || component.types.includes('administrative_area_level_3')) {
            comunaExtraida = component.long_name
            break
          }
        }

        if (onDireccionChange) {
          onDireccionChange(place.formatted_address, comunaExtraida)
        }
      } else {
        setError('No se encontró la dirección')
      }
    } catch (error) {
      console.error('Error en geocodificación:', error)
      setError('Error al buscar la dirección')
    } finally {
      setLoadingGeocoding(false)
    }
  }

  if (!googleMapsLoaded) {
    return (
      <div className="space-y-2">
        <label className="block text-sm font-medium text-gray-700">
          Dirección de Entrega
        </label>
        <div className="flex items-center gap-2 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
          <span className="text-sm text-blue-700">Cargando Google Maps...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">
        <MapPin className="inline h-4 w-4 mr-1" />
        Dirección de Entrega
      </label>

      {error && (
        <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg">
          <AlertCircle className="h-5 w-5 text-red-600" />
          <span className="text-sm text-red-700">{error}</span>
        </div>
      )}

      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={direccion}
          onChange={(e) => onDireccionChange && onDireccionChange(e.target.value, comuna)}
          placeholder="Escribe o selecciona una dirección..."
          className="w-full px-4 py-2 pr-10 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
        />
        {loadingGeocoding && (
          <Loader2 className="absolute right-3 top-1/2 transform -translate-y-1/2 h-5 w-5 animate-spin text-gray-400" />
        )}
      </div>

      <button
        type="button"
        onClick={geocodeDireccion}
        disabled={!direccion || loadingGeocoding}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2 transition-colors"
      >
        <Navigation className="h-4 w-4" />
        {loadingGeocoding ? 'Buscando...' : 'Buscar en el mapa'}
      </button>

      {/* Mapa */}
      <div
        ref={mapContainerRef}
        className="w-full h-64 rounded-lg border-2 border-gray-300 overflow-hidden"
      />

      <div className="text-xs text-gray-500">
        <strong>Tip:</strong> Puedes arrastrar el marcador rojo en el mapa para ajustar la ubicación exacta
      </div>

      {comuna && (
        <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-800">
            <strong>Comuna detectada:</strong> {comuna}
          </p>
        </div>
      )}

      {latitud && longitud && (
        <div className="text-xs text-gray-400">
          Coordenadas: {latitud.toFixed(6)}, {longitud.toFixed(6)}
        </div>
      )}
    </div>
  )
}

export default DireccionConMapa
