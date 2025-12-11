import { useState } from 'react'
import { usePendingApprovals, useApproveCluster, useRejectCluster } from '../lib/queries'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import Modal from '../components/Modal'
import { CheckCircle, XCircle, Eye, Layers } from 'lucide-react'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'

export default function ApprovalsPage() {
  const { data: pendingClusters, isLoading } = usePendingApprovals()
  const approveMutation = useApproveCluster()
  const rejectMutation = useRejectCluster()

  const [rejectModal, setRejectModal] = useState<{ clusterId: string; isOpen: boolean }>({
    clusterId: '',
    isOpen: false,
  })
  const [rejectReason, setRejectReason] = useState('')

  const handleApprove = async (clusterId: string) => {
    try {
      await approveMutation.mutateAsync({ clusterId })
      toast.success('Cluster approved')
    } catch {
      toast.error('Failed to approve cluster')
    }
  }

  const handleReject = async () => {
    if (!rejectReason.trim()) {
      toast.error('Please provide a reason')
      return
    }
    try {
      await rejectMutation.mutateAsync({
        clusterId: rejectModal.clusterId,
        reason: rejectReason,
      })
      toast.success('Cluster rejected')
      setRejectModal({ clusterId: '', isOpen: false })
      setRejectReason('')
    } catch {
      toast.error('Failed to reject cluster')
    }
  }

  if (isLoading) {
    return <LoadingSpinner className="h-64" />
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Pending Approvals</h1>
        <span className="badge-warning">{pendingClusters?.length || 0} pending</span>
      </div>

      {pendingClusters?.length ? (
        <div className="space-y-4">
          {pendingClusters.map((cluster) => (
            <div key={cluster.id} className="card">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Layers className="w-5 h-5 text-primary-600" />
                    <h3 className="font-semibold">{cluster.name}</h3>
                  </div>
                  {cluster.description && (
                    <p className="text-gray-600 mb-3">{cluster.description}</p>
                  )}
                  <div className="flex items-center gap-4 text-sm text-gray-500">
                    <span>{cluster.ticket_count} tickets</span>
                    <span>Created {new Date(cluster.created_at).toLocaleDateString()}</span>
                  </div>
                  {cluster.common_themes?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mt-3">
                      {cluster.common_themes.map((theme, i) => (
                        <span key={i} className="badge-info text-xs">
                          {theme}
                        </span>
                      ))}
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2 ml-4">
                  <Link
                    to={`/clusters/${cluster.id}`}
                    className="p-2 hover:bg-gray-100 rounded-lg text-gray-600"
                    title="View Details"
                  >
                    <Eye className="w-5 h-5" />
                  </Link>
                  <button
                    onClick={() => handleApprove(cluster.id)}
                    disabled={approveMutation.isPending}
                    className="p-2 hover:bg-green-100 rounded-lg text-green-600"
                    title="Approve"
                  >
                    <CheckCircle className="w-5 h-5" />
                  </button>
                  <button
                    onClick={() => setRejectModal({ clusterId: cluster.id, isOpen: true })}
                    className="p-2 hover:bg-red-100 rounded-lg text-red-600"
                    title="Reject"
                  >
                    <XCircle className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {cluster.suggested_resolution && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm font-medium text-gray-700 mb-1">Suggested Resolution</p>
                  <p className="text-sm text-gray-600">{cluster.suggested_resolution}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={CheckCircle}
          title="All caught up!"
          description="No clusters pending approval at the moment"
        />
      )}

      {/* Reject Modal */}
      <Modal
        isOpen={rejectModal.isOpen}
        onClose={() => setRejectModal({ clusterId: '', isOpen: false })}
        title="Reject Cluster"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Please provide a reason for rejecting this cluster. This feedback will help
            improve future clustering results.
          </p>
          <textarea
            value={rejectReason}
            onChange={(e) => setRejectReason(e.target.value)}
            placeholder="Reason for rejection..."
            className="input min-h-24"
          />
          <div className="flex justify-end gap-2">
            <button
              onClick={() => setRejectModal({ clusterId: '', isOpen: false })}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              onClick={handleReject}
              disabled={rejectMutation.isPending}
              className="btn-danger flex items-center gap-2"
            >
              {rejectMutation.isPending && <LoadingSpinner size="sm" />}
              Reject
            </button>
          </div>
        </div>
      </Modal>
    </div>
  )
}
