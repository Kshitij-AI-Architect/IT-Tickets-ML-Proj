export interface User {
  id: string
  email: string
  name: string
  role: 'admin' | 'po' | 'sme' | 'viewer'
  org_id: string
}

export interface Organization {
  id: string
  name: string
  settings: Record<string, unknown>
}

export interface Ticket {
  id: string
  external_id: string
  title: string
  description: string
  category?: string
  priority?: string
  status?: string
  created_date?: string
  resolved_date?: string
  resolution?: string
  metadata: Record<string, unknown>
  cluster_id?: string
  org_id: string
}

export interface Cluster {
  id: string
  name: string
  description?: string
  ticket_count: number
  common_themes: string[]
  suggested_resolution?: string
  status: 'pending' | 'reviewed' | 'approved' | 'rejected'
  created_at: string
  org_id: string
  tickets?: Ticket[]
}

export interface Assessment {
  id: string
  cluster_id: string
  question: string
  answer: string
  confidence: number
  sources: string[]
  created_at: string
  feedback?: AssessmentFeedback
}

export interface AssessmentFeedback {
  id: string
  assessment_id: string
  rating: 'helpful' | 'not_helpful' | 'incorrect'
  corrected_answer?: string
  comments?: string
  submitted_by: string
  created_at: string
}

export interface KnowledgeEntry {
  id: string
  title: string
  content: string
  source_type: 'feedback' | 'document' | 'manual'
  source_id?: string
  tags: string[]
  created_at: string
  org_id: string
}

export interface SchemaMapping {
  id: string
  name: string
  source_type: string
  field_mappings: Record<string, string>
  org_id: string
}

export interface UploadResult {
  success: boolean
  tickets_created: number
  errors: string[]
}

export interface AnalyticsData {
  total_tickets: number
  total_clusters: number
  pending_approvals: number
  knowledge_entries: number
  tickets_by_category: Record<string, number>
  clusters_by_status: Record<string, number>
  recent_activity: ActivityItem[]
}

export interface ActivityItem {
  id: string
  type: 'upload' | 'cluster' | 'approval' | 'feedback'
  description: string
  timestamp: string
  user?: string
}
