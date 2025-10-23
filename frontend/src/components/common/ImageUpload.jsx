import { useState, useRef } from 'react'
import { Upload, X, Image as ImageIcon } from 'lucide-react'
import axios from 'axios'

function ImageUpload({ currentImage, onImageUpdate, itemType, itemId, label = "Foto" }) {
  const [uploading, setUploading] = useState(false)
  const [preview, setPreview] = useState(currentImage)
  const fileInputRef = useRef(null)
  
  const handleFileSelect = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    
    // Validar tipo de archivo
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
    if (!validTypes.includes(file.type)) {
      alert('Por favor selecciona una imagen válida (JPG, PNG, GIF o WebP)')
      return
    }
    
    // Validar tamaño (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      alert('La imagen no debe pesar más de 5MB')
      return
    }
    
    try {
      setUploading(true)
      
      // Crear FormData
      const formData = new FormData()
      formData.append('file', file)
      
      // Subir imagen
      const response = await axios.post(
        `/api/upload/${itemType}/${itemId}/foto`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )
      
      if (response.data.success) {
        const newImageUrl = response.data.data.foto_url || response.data.data.imagen_url
        setPreview(newImageUrl)
        if (onImageUpdate) onImageUpdate(newImageUrl)
      }
      
    } catch (error) {
      console.error('Error al subir imagen:', error)
      alert('Error al subir la imagen')
    } finally {
      setUploading(false)
    }
  }
  
  const handleRemoveImage = async () => {
    if (!confirm('¿Eliminar la imagen actual?')) return
    
    try {
      // Enviar null para eliminar
      await axios.post(`/api/upload/${itemType}/${itemId}/foto`, {
        foto_url: null
      })
      
      setPreview(null)
      if (onImageUpdate) onImageUpdate(null)
    } catch (error) {
      console.error('Error al eliminar imagen:', error)
      alert('Error al eliminar la imagen')
    }
  }
  
  return (
    <div className="space-y-2">
      <label className="block text-sm font-medium text-gray-700">
        {label}
      </label>
      
      <div className="flex items-center gap-4">
        {/* Preview */}
        <div className="relative w-24 h-24 bg-gray-100 rounded-lg border-2 border-dashed border-gray-300 flex items-center justify-center overflow-hidden">
          {preview ? (
            <img
              src={preview.startsWith('http') ? preview : `/api/upload/imagen/${preview}`}
              alt="Preview"
              className="w-full h-full object-cover"
            />
          ) : (
            <ImageIcon className="h-10 w-10 text-gray-400" />
          )}
          
          {/* Loading overlay */}
          {uploading && (
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
            </div>
          )}
        </div>
        
        {/* Botones */}
        <div className="flex flex-col gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleFileSelect}
            className="hidden"
          />
          
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:bg-gray-400 flex items-center gap-2 text-sm"
          >
            <Upload className="h-4 w-4" />
            {preview ? 'Cambiar' : 'Subir'}
          </button>
          
          {preview && (
            <button
              type="button"
              onClick={handleRemoveImage}
              className="px-4 py-2 bg-red-100 text-red-700 rounded-lg hover:bg-red-200 flex items-center gap-2 text-sm"
            >
              <X className="h-4 w-4" />
              Eliminar
            </button>
          )}
        </div>
      </div>
      
      <p className="text-xs text-gray-500">
        JPG, PNG, GIF o WebP. Máximo 5MB.
      </p>
    </div>
  )
}

export default ImageUpload

