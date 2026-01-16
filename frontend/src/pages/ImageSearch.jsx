/**
 * Página de búsqueda por imagen.
 */
import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Search, Image, ExternalLink, Loader, FileText } from 'lucide-react'
import toast from 'react-hot-toast'
import Layout from '../components/Layout'
import { imagesAPI } from '../services/api'

function ImageSearch() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [isSearching, setIsSearching] = useState(false)
  const [results, setResults] = useState(null)
  const [ocrText, setOcrText] = useState(null)

  const onDrop = useCallback((acceptedFiles) => {
    const selectedFile = acceptedFiles[0]
    if (selectedFile) {
      setFile(selectedFile)
      setPreview(URL.createObjectURL(selectedFile))
      setResults(null)
      setOcrText(null)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.png', '.jpg', '.jpeg', '.webp'],
    },
    maxSize: 5 * 1024 * 1024, // 5MB
    multiple: false,
  })

  const handleSearch = async () => {
    if (!file) {
      toast.error('Selecciona una imagen')
      return
    }

    setIsSearching(true)
    try {
      const response = await imagesAPI.searchByImage(file)
      setResults(response.data)

      if (!response.data.success) {
        toast.error(response.data.error || 'Error en la búsqueda')
      }
    } catch (error) {
      toast.error('Error al buscar')
    } finally {
      setIsSearching(false)
    }
  }

  const handleOCR = async () => {
    if (!file) {
      toast.error('Selecciona una imagen')
      return
    }

    setIsSearching(true)
    try {
      const response = await imagesAPI.extractText(file)
      setOcrText(response.data)

      if (!response.data.success) {
        toast.error(response.data.error || 'Error en OCR')
      }
    } catch (error) {
      toast.error('Error al extraer texto')
    } finally {
      setIsSearching(false)
    }
  }

  const clearAll = () => {
    setFile(null)
    setPreview(null)
    setResults(null)
    setOcrText(null)
  }

  return (
    <Layout title="Búsqueda por imagen">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Panel de subida */}
        <div className="card">
          <div className="card-header">
            <h2 className="font-semibold text-gray-800">Subir imagen</h2>
          </div>
          <div className="card-body">
            {/* Dropzone */}
            <div
              {...getRootProps()}
              className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
                isDragActive
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-300 hover:border-primary-400'
              }`}
            >
              <input {...getInputProps()} />

              {preview ? (
                <div className="space-y-4">
                  <img
                    src={preview}
                    alt="Preview"
                    className="max-h-64 mx-auto rounded-lg shadow"
                  />
                  <p className="text-sm text-gray-500">{file.name}</p>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto">
                    <Upload size={28} className="text-gray-400" />
                  </div>
                  <div>
                    <p className="text-gray-700 font-medium">
                      Arrastra una imagen aquí
                    </p>
                    <p className="text-sm text-gray-500">
                      o haz clic para seleccionar
                    </p>
                  </div>
                  <p className="text-xs text-gray-400">
                    PNG, JPG, WEBP hasta 5MB
                  </p>
                </div>
              )}
            </div>

            {/* Botones de acción */}
            {file && (
              <div className="flex flex-wrap gap-3 mt-4">
                <button
                  onClick={handleSearch}
                  disabled={isSearching}
                  className="btn-primary flex-1"
                >
                  {isSearching ? (
                    <Loader size={18} className="animate-spin" />
                  ) : (
                    <Search size={18} />
                  )}
                  Buscar producto
                </button>
                <button
                  onClick={handleOCR}
                  disabled={isSearching}
                  className="btn-secondary flex-1"
                >
                  {isSearching ? (
                    <Loader size={18} className="animate-spin" />
                  ) : (
                    <FileText size={18} />
                  )}
                  Extraer texto (OCR)
                </button>
                <button onClick={clearAll} className="btn-secondary">
                  Limpiar
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Panel de resultados */}
        <div className="space-y-6">
          {/* Resultados de búsqueda de imagen */}
          {results && (
            <div className="card">
              <div className="card-header">
                <h2 className="font-semibold text-gray-800">Resultados de búsqueda</h2>
              </div>
              <div className="card-body space-y-6">
                {/* Etiquetas detectadas */}
                {results.labels && results.labels.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">
                      Objetos detectados
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {results.labels.map((label, i) => (
                        <span key={i} className="badge badge-blue">
                          {label.description} ({label.score}%)
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Entidades web */}
                {results.web_entities && results.web_entities.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">
                      Identificación
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {results.web_entities.map((entity, i) => (
                        <span key={i} className="badge badge-green">
                          {entity.description}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Páginas donde aparece */}
                {results.pages_with_image && results.pages_with_image.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">
                      Páginas donde aparece esta imagen
                    </h3>
                    <div className="space-y-2">
                      {results.pages_with_image.map((page, i) => (
                        <a
                          key={i}
                          href={page.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg hover:bg-gray-100"
                        >
                          <Image size={16} className="text-gray-400" />
                          <span className="flex-1 truncate text-sm text-gray-700">
                            {page.title || page.url}
                          </span>
                          <ExternalLink size={14} className="text-gray-400" />
                        </a>
                      ))}
                    </div>
                  </div>
                )}

                {/* Texto detectado */}
                {results.text_detected && (
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 mb-2">
                      Texto detectado en la imagen
                    </h3>
                    <div className="p-3 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-700 whitespace-pre-wrap">
                        {results.text_detected}
                      </p>
                    </div>
                  </div>
                )}

                {/* Sin resultados */}
                {!results.labels?.length &&
                  !results.web_entities?.length &&
                  !results.pages_with_image?.length && (
                    <div className="empty-state py-8">
                      <Image size={32} className="text-gray-400 mb-2" />
                      <p>No se encontraron resultados para esta imagen</p>
                    </div>
                  )}
              </div>
            </div>
          )}

          {/* Resultados de OCR */}
          {ocrText && (
            <div className="card">
              <div className="card-header">
                <h2 className="font-semibold text-gray-800">
                  Texto extraído (OCR)
                  {ocrText.confidence > 0 && (
                    <span className="ml-2 text-sm text-gray-500">
                      Confianza: {ocrText.confidence}%
                    </span>
                  )}
                </h2>
              </div>
              <div className="card-body space-y-4">
                {ocrText.raw_text ? (
                  <>
                    <div className="p-4 bg-gray-50 rounded-lg">
                      <p className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
                        {ocrText.raw_text}
                      </p>
                    </div>

                    {/* Emails encontrados */}
                    {ocrText.emails && ocrText.emails.length > 0 && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-2">
                          Emails detectados
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {ocrText.emails.map((email, i) => (
                            <span key={i} className="badge badge-blue">
                              {email}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Teléfonos encontrados */}
                    {ocrText.phones && ocrText.phones.length > 0 && (
                      <div>
                        <h3 className="text-sm font-medium text-gray-700 mb-2">
                          Teléfonos detectados
                        </h3>
                        <div className="flex flex-wrap gap-2">
                          {ocrText.phones.map((phone, i) => (
                            <span key={i} className="badge badge-green">
                              {phone}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="empty-state py-8">
                    <FileText size={32} className="text-gray-400 mb-2" />
                    <p>No se detectó texto en la imagen</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Estado inicial */}
          {!results && !ocrText && (
            <div className="card">
              <div className="card-body empty-state py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                  <Search size={28} className="text-gray-400" />
                </div>
                <h3 className="text-lg font-medium text-gray-700 mb-2">
                  Busca por imagen
                </h3>
                <p className="text-gray-500 text-center max-w-sm">
                  Sube una foto de un producto para encontrar empresas que lo vendan
                  o extrae texto de capturas de pantalla.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  )
}

export default ImageSearch
