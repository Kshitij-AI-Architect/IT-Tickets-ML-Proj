import { useAssessments } from '../lib/queries'
import LoadingSpinner from '../components/LoadingSpinner'
import EmptyState from '../components/EmptyState'
import { FileSearch, ThumbsUp, ThumbsDown, ExternalLink } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function AssessmentsPage() {
  const { data: assessments, isLoading } = useAssessments()

  if (isLoading) {
    return <LoadingSpinner className="h-64" />
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Assessments</h1>

      {assessments?.length ? (
        <div className="space-y-4">
          {assessments.map((assessment) => (
            <div key={assessment.id} className="card">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <p className="font-medium text-primary-700">Q: {assessment.question}</p>
                  <Link
                    to={`/clusters/${assessment.cluster_id}`}
                    className="text-xs text-gray-500 hover:text-primary-600 flex items-center gap-1 mt-1"
                  >
                    View Cluster <ExternalLink className="w-3 h-3" />
                  </Link>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(assessment.created_at).toLocaleDateString()}
                </span>
              </div>

              <p className="text-gray-700 mb-4">{assessment.answer}</p>

              <div className="flex items-center justify-between pt-3 border-t">
                <div className="flex items-center gap-4 text-sm text-gray-500">
                  <span>Confidence: {(assessment.confidence * 100).toFixed(0)}%</span>
                  {assessment.sources?.length > 0 && (
                    <span>{assessment.sources.length} sources</span>
                  )}
                </div>

                {assessment.feedback ? (
                  <div className="flex items-center gap-2">
                    {assessment.feedback.rating === 'helpful' ? (
                      <span className="badge-success flex items-center gap-1">
                        <ThumbsUp className="w-3 h-3" /> Helpful
                      </span>
                    ) : (
                      <span className="badge-error flex items-center gap-1">
                        <ThumbsDown className="w-3 h-3" /> {assessment.feedback.rating}
                      </span>
                    )}
                  </div>
                ) : (
                  <span className="text-xs text-gray-400">No feedback yet</span>
                )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={FileSearch}
          title="No assessments yet"
          description="Generate assessments by asking questions about ticket clusters"
        />
      )}
    </div>
  )
}
