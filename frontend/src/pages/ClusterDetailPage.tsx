import { useParams, useNavigate } from 'react-router-dom'
import { useCluster, useAssessments, useGenerateAssessment, useSubmitFeedback } from '../lib/queries'
import LoadingSpinner from '../components/LoadingSpinner'
import StatusBadge from '../components/StatusBadge'
import Modal from '../components/Modal'
import { useState } from 'react'
import { ArrowLeft, MessageSquare, ThumbsUp, ThumbsDown, AlertCircle, Send } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ClusterDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [showAssessmentModal, setShowAssessmentModal] = useState(false)
  const [question, setQuestion] = useState('')
  const [feedbackModal, setFeedbackModal] = useState<{ assessmentId: string; isOpen: boolean }>({
    assessmentId: '',
    isOpen: false,
  })

  const { data: cluster, isLoading: clusterLoading } = useCluster(id!)
  const { data: assessments, isLoading: assessmentsLoading } = useAssessments(id)
  const generateMutation = useGenerateAssessment()
  const feedbackMutation = useSubmitFeedback()

  const handleGenerateAssessment = async () => {
    if (!question.trim() || !id) return
    try {
      await generateMutation.mutateAsync({ clusterId: id, question })
      toast.success('Assessment generated')
      setQuestion('')
      setShowAssessmentModal(false)
    } catch {
      toast.error('Failed to generate assessment')
    }
  }

  const handleFeedback = async (rating: string, correctedAnswer?: string) => {
    try {
      await feedbackMutation.mutateAsync({
        assessment_id: feedbackModal.assessmentId,
        rating,
        corrected_answer: correctedAnswer,
      })
      toast.success('Feedback submitted')
      setFeedbackModal({ assessmentId: '', isOpen: false })
    } catch {
      toast.error('Failed to submit feedback')
    }
  }

  if (clusterLoading) {
    return <LoadingSpinner className="h-64" />
  }

  if (!cluster) {
    return <div>Cluster not found</div>
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button onClick={() => navigate('/clusters')} className="p-2 hover:bg-gray-100 rounded-lg">
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold">{cluster.name}</h1>
            <StatusBadge status={cluster.status} />
          </div>
          {cluster.description && (
            <p className="text-gray-600 mt-1">{cluster.description}</p>
          )}
        </div>
        <button
          onClick={() => setShowAssessmentModal(true)}
          className="btn-primary flex items-center gap-2"
        >
          <MessageSquare className="w-4 h-4" />
          Ask Question
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Tickets */}
        <div className="lg:col-span-2 space-y-4">
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">
              Tickets ({cluster.ticket_count})
            </h2>
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {cluster.tickets?.map((ticket) => (
                <div key={ticket.id} className="p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-start justify-between">
                    <h4 className="font-medium">{ticket.title}</h4>
                    {ticket.priority && (
                      <span className="badge-info text-xs">{ticket.priority}</span>
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                    {ticket.description}
                  </p>
                </div>
              )) || <p className="text-gray-500">No tickets loaded</p>}
            </div>
          </div>

          {/* Assessments */}
          <div className="card">
            <h2 className="text-lg font-semibold mb-4">Assessments</h2>
            {assessmentsLoading ? (
              <LoadingSpinner />
            ) : assessments?.length ? (
              <div className="space-y-4">
                {assessments.map((assessment) => (
                  <div key={assessment.id} className="border rounded-lg p-4">
                    <p className="font-medium text-primary-700 mb-2">
                      Q: {assessment.question}
                    </p>
                    <p className="text-gray-700 mb-3">{assessment.answer}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        Confidence: {(assessment.confidence * 100).toFixed(0)}%
                      </span>
                      <div className="flex gap-2">
                        <button
                          onClick={() =>
                            handleFeedback('helpful')
                          }
                          className="p-1 hover:bg-green-100 rounded text-green-600"
                          title="Helpful"
                        >
                          <ThumbsUp className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() =>
                            setFeedbackModal({ assessmentId: assessment.id, isOpen: true })
                          }
                          className="p-1 hover:bg-red-100 rounded text-red-600"
                          title="Not helpful"
                        >
                          <ThumbsDown className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-4">
                No assessments yet. Ask a question to get started.
              </p>
            )}
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-4">
          <div className="card">
            <h3 className="font-semibold mb-3">Common Themes</h3>
            <div className="flex flex-wrap gap-2">
              {cluster.common_themes?.map((theme, i) => (
                <span key={i} className="badge-info">
                  {theme}
                </span>
              )) || <p className="text-gray-500 text-sm">No themes identified</p>}
            </div>
          </div>

          {cluster.suggested_resolution && (
            <div className="card">
              <h3 className="font-semibold mb-3">Suggested Resolution</h3>
              <p className="text-sm text-gray-700">{cluster.suggested_resolution}</p>
            </div>
          )}
        </div>
      </div>

      {/* Ask Question Modal */}
      <Modal
        isOpen={showAssessmentModal}
        onClose={() => setShowAssessmentModal(false)}
        title="Ask a Question"
      >
        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Ask a question about this cluster. The AI will analyze the tickets and provide
            a grounded response.
          </p>
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., What is the root cause of these issues?"
            className="input min-h-24"
          />
          <div className="flex justify-end gap-2">
            <button onClick={() => setShowAssessmentModal(false)} className="btn-secondary">
              Cancel
            </button>
            <button
              onClick={handleGenerateAssessment}
              disabled={!question.trim() || generateMutation.isPending}
              className="btn-primary flex items-center gap-2"
            >
              {generateMutation.isPending ? <LoadingSpinner size="sm" /> : <Send className="w-4 h-4" />}
              Generate
            </button>
          </div>
        </div>
      </Modal>

      {/* Feedback Modal */}
      <FeedbackModal
        isOpen={feedbackModal.isOpen}
        onClose={() => setFeedbackModal({ assessmentId: '', isOpen: false })}
        onSubmit={(rating, corrected) => handleFeedback(rating, corrected)}
      />
    </div>
  )
}

function FeedbackModal({
  isOpen,
  onClose,
  onSubmit,
}: {
  isOpen: boolean
  onClose: () => void
  onSubmit: (rating: string, correctedAnswer?: string) => void
}) {
  const [rating, setRating] = useState<string>('not_helpful')
  const [correctedAnswer, setCorrectedAnswer] = useState('')

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Provide Feedback">
      <div className="space-y-4">
        <div className="flex items-start gap-2 p-3 bg-yellow-50 rounded-lg">
          <AlertCircle className="w-5 h-5 text-yellow-600 flex-shrink-0" />
          <p className="text-sm text-yellow-800">
            Your feedback helps improve future responses. If the answer was incorrect,
            please provide the correct information.
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Rating</label>
          <select value={rating} onChange={(e) => setRating(e.target.value)} className="input">
            <option value="not_helpful">Not Helpful</option>
            <option value="incorrect">Incorrect</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Corrected Answer (Optional)</label>
          <textarea
            value={correctedAnswer}
            onChange={(e) => setCorrectedAnswer(e.target.value)}
            placeholder="Provide the correct answer..."
            className="input min-h-24"
          />
        </div>

        <div className="flex justify-end gap-2">
          <button onClick={onClose} className="btn-secondary">
            Cancel
          </button>
          <button onClick={() => onSubmit(rating, correctedAnswer)} className="btn-primary">
            Submit Feedback
          </button>
        </div>
      </div>
    </Modal>
  )
}
