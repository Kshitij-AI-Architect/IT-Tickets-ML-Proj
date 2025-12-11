import { useState } from 'react'
import { useKnowledge, useAddKnowledge } from '../lib/queries'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import Modal from '../components/Modal'
import { BookOpen, Plus, Search, Tag } from 'lucide-react'
import toast from 'react-hot-toast'

export default function KnowledgePage() {
  const [search, setSearch] = useState('')
  const [showAddModal, setShowAddModal] = useState(false)

  const { data: knowledge, isLoading } = useKnowledge()
  const addMutation = useAddKnowledge()

  const filteredKnowledge = knowledge?.filter(
    (k) =>
      k.title.toLowerCase().includes(search.toLowerCase()) ||
      k.content.toLowerCase().includes(search.toLowerCase()) ||
      k.tags.some((t) => t.toLowerCase().includes(search.toLowerCase()))
  )

  const handleAdd = async (entry: { title: string; content: string; tags: string[] }) => {
    try {
      await addMutation.mutateAsync({
        ...entry,
        source_type: 'manual',
      })
      toast.success('Knowledge entry added')
      setShowAddModal(false)
    } catch {
      toast.error('Failed to add entry')
    }
  }

  if (isLoading) {
    return <LoadingSpinner className="h-64" />
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <h1 className="text-2xl font-bold">Knowledge Base</h1>
        <button
          onClick={() => setShowAddModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add Entry
        </button>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search knowledge base..."
          className="input pl-10"
        />
      </div>

      {/* Knowledge Entries */}
      {filteredKnowledge?.length ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {filteredKnowledge.map((entry) => (
            <div key={entry.id} className="card">
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold">{entry.title}</h3>
                <span className="text-xs text-gray-500 capitalize">{entry.source_type}</span>
              </div>
              <p className="text-sm text-gray-600 mb-3 line-clamp-3">{entry.content}</p>
              <div className="flex items-center justify-between">
                <div className="flex flex-wrap gap-1">
                  {entry.tags.map((tag, i) => (
                    <span key={i} className="badge-info text-xs flex items-center gap-1">
                      <Tag className="w-3 h-3" />
                      {tag}
                    </span>
                  ))}
                </div>
                <span className="text-xs text-gray-400">
                  {new Date(entry.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={BookOpen}
          title="No knowledge entries"
          description="Add entries manually or they'll be created from SME feedback"
          action={{ label: 'Add Entry', onClick: () => setShowAddModal(true) }}
        />
      )}

      {/* Add Modal */}
      <AddKnowledgeModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSave={handleAdd}
        isPending={addMutation.isPending}
      />
    </div>
  )
}

function AddKnowledgeModal({
  isOpen,
  onClose,
  onSave,
  isPending,
}: {
  isOpen: boolean
  onClose: () => void
  onSave: (entry: { title: string; content: string; tags: string[] }) => void
  isPending: boolean
}) {
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [tagsInput, setTagsInput] = useState('')

  const handleSave = () => {
    const tags = tagsInput
      .split(',')
      .map((t) => t.trim())
      .filter(Boolean)
    onSave({ title, content, tags })
    setTitle('')
    setContent('')
    setTagsInput('')
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add Knowledge Entry" size="lg">
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="input"
            placeholder="Entry title"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Content</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="input min-h-32"
            placeholder="Knowledge content..."
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Tags (comma-separated)
          </label>
          <input
            type="text"
            value={tagsInput}
            onChange={(e) => setTagsInput(e.target.value)}
            className="input"
            placeholder="e.g., networking, vpn, troubleshooting"
          />
        </div>

        <div className="flex justify-end gap-2 pt-4">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button
            onClick={handleSave}
            disabled={!title || !content || isPending}
            className="btn-primary flex items-center gap-2"
          >
            {isPending && <LoadingSpinner size="sm" />}
            Add Entry
          </button>
        </div>
      </div>
    </Modal>
  )
}
