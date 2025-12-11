import { useState, useCallback } from 'react'
import { useUploadTickets, useSchemaMappings, useCreateSchemaMapping } from '../lib/queries'
import toast from 'react-hot-toast'
import { Upload, FileSpreadsheet, Plus, Check, AlertCircle } from 'lucide-react'
import Modal from '../components/Modal'
import LoadingSpinner from '../components/LoadingSpinner'

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null)
  const [selectedMapping, setSelectedMapping] = useState<string>('')
  const [showMappingModal, setShowMappingModal] = useState(false)
  const [dragActive, setDragActive] = useState(false)

  const { data: mappings, isLoading: mappingsLoading } = useSchemaMappings()
  const uploadMutation = useUploadTickets()
  const createMappingMutation = useCreateSchemaMapping()

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)
    if (e.dataTransfer.files?.[0]) {
      setFile(e.dataTransfer.files[0])
    }
  }, [])

  const handleUpload = async () => {
    if (!file) return

    const formData = new FormData()
    formData.append('file', file)
    if (selectedMapping) {
      formData.append('schema_mapping_id', selectedMapping)
    }

    try {
      const result = await uploadMutation.mutateAsync(formData)
      toast.success(`Successfully uploaded ${result.tickets_created} tickets`)
      setFile(null)
    } catch {
      toast.error('Upload failed')
    }
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Upload Tickets</h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Upload Area */}
        <div className="lg:col-span-2">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Upload File</h2>

            <div
              className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                dragActive ? 'border-primary-500 bg-primary-50' : 'border-gray-300'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              {file ? (
                <div className="flex items-center justify-center gap-3">
                  <FileSpreadsheet className="w-8 h-8 text-primary-600" />
                  <div className="text-left">
                    <p className="font-medium">{file.name}</p>
                    <p className="text-sm text-gray-500">
                      {(file.size / 1024).toFixed(1)} KB
                    </p>
                  </div>
                  <button
                    onClick={() => setFile(null)}
                    className="ml-4 text-gray-400 hover:text-gray-600"
                  >
                    ×
                  </button>
                </div>
              ) : (
                <>
                  <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-600 mb-2">
                    Drag and drop your file here, or{' '}
                    <label className="text-primary-600 cursor-pointer hover:underline">
                      browse
                      <input
                        type="file"
                        className="hidden"
                        accept=".csv,.xlsx,.json"
                        onChange={(e) => setFile(e.target.files?.[0] || null)}
                      />
                    </label>
                  </p>
                  <p className="text-sm text-gray-400">Supports CSV, Excel, and JSON</p>
                </>
              )}
            </div>

            {/* Schema Mapping Selection */}
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Schema Mapping (Optional)
              </label>
              <div className="flex gap-2">
                <select
                  value={selectedMapping}
                  onChange={(e) => setSelectedMapping(e.target.value)}
                  className="input flex-1"
                  disabled={mappingsLoading}
                >
                  <option value="">Auto-detect schema</option>
                  {mappings?.map((m) => (
                    <option key={m.id} value={m.id}>
                      {m.name}
                    </option>
                  ))}
                </select>
                <button
                  onClick={() => setShowMappingModal(true)}
                  className="btn-secondary flex items-center gap-1"
                >
                  <Plus className="w-4 h-4" />
                  New
                </button>
              </div>
            </div>

            <button
              onClick={handleUpload}
              disabled={!file || uploadMutation.isPending}
              className="btn-primary w-full mt-6 flex items-center justify-center gap-2"
            >
              {uploadMutation.isPending ? (
                <LoadingSpinner size="sm" />
              ) : (
                <Upload className="w-4 h-4" />
              )}
              Upload Tickets
            </button>
          </div>
        </div>

        {/* Instructions */}
        <div className="card h-fit">
          <h2 className="text-lg font-semibold mb-4">Instructions</h2>
          <div className="space-y-3 text-sm">
            <div className="flex gap-2">
              <Check className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
              <p>Upload CSV, Excel, or JSON files containing ticket data</p>
            </div>
            <div className="flex gap-2">
              <Check className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
              <p>Required fields: title, description</p>
            </div>
            <div className="flex gap-2">
              <Check className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
              <p>Optional: category, priority, status, dates</p>
            </div>
            <div className="flex gap-2">
              <AlertCircle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
              <p>Create a schema mapping for non-standard column names</p>
            </div>
          </div>
        </div>
      </div>

      {/* Schema Mapping Modal */}
      <SchemaMappingModal
        isOpen={showMappingModal}
        onClose={() => setShowMappingModal(false)}
        onSave={async (mapping) => {
          await createMappingMutation.mutateAsync(mapping)
          toast.success('Schema mapping created')
          setShowMappingModal(false)
        }}
      />
    </div>
  )
}

function SchemaMappingModal({
  isOpen,
  onClose,
  onSave,
}: {
  isOpen: boolean
  onClose: () => void
  onSave: (mapping: { name: string; source_type: string; field_mappings: Record<string, string> }) => void
}) {
  const [name, setName] = useState('')
  const [sourceType, setSourceType] = useState('csv')
  const [mappings, setMappings] = useState<Record<string, string>>({
    title: '',
    description: '',
    category: '',
    priority: '',
    status: '',
  })

  const handleSave = () => {
    const filteredMappings = Object.fromEntries(
      Object.entries(mappings).filter(([, v]) => v)
    )
    onSave({ name, source_type: sourceType, field_mappings: filteredMappings })
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Schema Mapping" size="lg">
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="input"
            placeholder="e.g., ServiceNow Export"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Source Type</label>
          <select
            value={sourceType}
            onChange={(e) => setSourceType(e.target.value)}
            className="input"
          >
            <option value="csv">CSV</option>
            <option value="excel">Excel</option>
            <option value="json">JSON</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Field Mappings</label>
          <p className="text-xs text-gray-500 mb-3">
            Map your source column names to our standard fields
          </p>
          <div className="space-y-2">
            {Object.entries(mappings).map(([field, value]) => (
              <div key={field} className="flex items-center gap-2">
                <span className="w-24 text-sm text-gray-600 capitalize">{field}</span>
                <span className="text-gray-400">→</span>
                <input
                  type="text"
                  value={value}
                  onChange={(e) => setMappings({ ...mappings, [field]: e.target.value })}
                  className="input flex-1"
                  placeholder={`Source column for ${field}`}
                />
              </div>
            ))}
          </div>
        </div>

        <div className="flex justify-end gap-2 pt-4">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button onClick={handleSave} disabled={!name} className="btn-primary">
            Create Mapping
          </button>
        </div>
      </div>
    </Modal>
  )
}
