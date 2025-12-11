import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useClusters, useRunClustering } from '../lib/queries'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import StatusBadge from '../components/StatusBadge'
import { Layers, Play, Search, Filter } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ClustersPage() {
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [search, setSearch] = useState('')

  const { data: clusters, isLoading } = useClusters(statusFilter || undefined)
  const runClusteringMutation = useRunClustering()

  const handleRunClustering = async () => {
    try {
      await runClusteringMutation.mutateAsync()
      toast.success('Clustering completed')
    } catch {
      toast.error('Clustering failed')
    }
  }

  const filteredClusters = clusters?.filter(
    (c) =>
      c.name.toLowerCase().includes(search.toLowerCase()) ||
      c.description?.toLowerCase().includes(search.toLowerCase())
  )

  if (isLoading) {
    return <LoadingSpinner className="h-64" />
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <h1 className="text-2xl font-bold">Clusters</h1>
        <button
          onClick={handleRunClustering}
          disabled={runClusteringMutation.isPending}
          className="btn-primary flex items-center gap-2"
        >
          {runClusteringMutation.isPending ? (
            <LoadingSpinner size="sm" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          Run Clustering
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search clusters..."
            className="input pl-10"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="input w-40"
          >
            <option value="">All Status</option>
            <option value="pending">Pending</option>
            <option value="reviewed">Reviewed</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
          </select>
        </div>
      </div>

      {/* Clusters Grid */}
      {filteredClusters?.length ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredClusters.map((cluster) => (
            <Link
              key={cluster.id}
              to={`/clusters/${cluster.id}`}
              className="card hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Layers className="w-5 h-5 text-primary-600" />
                  <h3 className="font-semibold truncate">{cluster.name}</h3>
                </div>
                <StatusBadge status={cluster.status} />
              </div>

              {cluster.description && (
                <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                  {cluster.description}
                </p>
              )}

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">{cluster.ticket_count} tickets</span>
                <span className="text-gray-400">
                  {new Date(cluster.created_at).toLocaleDateString()}
                </span>
              </div>

              {cluster.common_themes?.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-3">
                  {cluster.common_themes.slice(0, 3).map((theme, i) => (
                    <span key={i} className="badge-info text-xs">
                      {theme}
                    </span>
                  ))}
                </div>
              )}
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Layers}
          title="No clusters found"
          description="Run clustering to group similar tickets together"
          action={{ label: 'Run Clustering', onClick: handleRunClustering }}
        />
      )}
    </div>
  )
}
