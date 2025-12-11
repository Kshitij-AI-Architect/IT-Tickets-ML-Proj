import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from './api'
import type {
  Cluster,
  Assessment,
  KnowledgeEntry,
  AnalyticsData,
  UploadResult,
  SchemaMapping,
} from '../types'

// Analytics
export function useAnalytics() {
  return useQuery<AnalyticsData>({
    queryKey: ['analytics'],
    queryFn: async () => {
      const { data } = await api.get('/analytics/dashboard')
      return data
    },
  })
}

// Clusters
export function useClusters(status?: string) {
  return useQuery<Cluster[]>({
    queryKey: ['clusters', status],
    queryFn: async () => {
      const params = status ? { status } : {}
      const { data } = await api.get('/clusters', { params })
      return data
    },
  })
}

export function useCluster(id: string) {
  return useQuery<Cluster>({
    queryKey: ['cluster', id],
    queryFn: async () => {
      const { data } = await api.get(`/clusters/${id}`)
      return data
    },
    enabled: !!id,
  })
}

export function useRunClustering() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async () => {
      const { data } = await api.post('/clusters/run')
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['clusters'] })
      queryClient.invalidateQueries({ queryKey: ['analytics'] })
    },
  })
}

// Assessments
export function useAssessments(clusterId?: string) {
  return useQuery<Assessment[]>({
    queryKey: ['assessments', clusterId],
    queryFn: async () => {
      const params = clusterId ? { cluster_id: clusterId } : {}
      const { data } = await api.get('/assessments', { params })
      return data
    },
  })
}

export function useGenerateAssessment() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ clusterId, question }: { clusterId: string; question: string }) => {
      const { data } = await api.post('/assessments/generate', {
        cluster_id: clusterId,
        question,
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessments'] })
    },
  })
}

export function useSubmitFeedback() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (feedback: {
      assessment_id: string
      rating: string
      corrected_answer?: string
      comments?: string
    }) => {
      const { data } = await api.post('/feedback', feedback)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessments'] })
      queryClient.invalidateQueries({ queryKey: ['knowledge'] })
    },
  })
}

// Approvals
export function usePendingApprovals() {
  return useQuery<Cluster[]>({
    queryKey: ['approvals', 'pending'],
    queryFn: async () => {
      const { data } = await api.get('/approval/pending')
      return data
    },
  })
}

export function useApproveCluster() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ clusterId, comments }: { clusterId: string; comments?: string }) => {
      const { data } = await api.post(`/approval/${clusterId}/approve`, { comments })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['approvals'] })
      queryClient.invalidateQueries({ queryKey: ['clusters'] })
      queryClient.invalidateQueries({ queryKey: ['analytics'] })
    },
  })
}

export function useRejectCluster() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ clusterId, reason }: { clusterId: string; reason: string }) => {
      const { data } = await api.post(`/approval/${clusterId}/reject`, { reason })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['approvals'] })
      queryClient.invalidateQueries({ queryKey: ['clusters'] })
    },
  })
}

// Knowledge
export function useKnowledge() {
  return useQuery<KnowledgeEntry[]>({
    queryKey: ['knowledge'],
    queryFn: async () => {
      const { data } = await api.get('/knowledge')
      return data
    },
  })
}

export function useAddKnowledge() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (entry: Partial<KnowledgeEntry>) => {
      const { data } = await api.post('/knowledge', entry)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['knowledge'] })
    },
  })
}

// Upload
export function useUploadTickets() {
  const queryClient = useQueryClient()
  return useMutation<UploadResult, Error, FormData>({
    mutationFn: async (formData) => {
      const { data } = await api.post('/upload/tickets', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['analytics'] })
    },
  })
}

// Schema Mappings
export function useSchemaMappings() {
  return useQuery<SchemaMapping[]>({
    queryKey: ['schema-mappings'],
    queryFn: async () => {
      const { data } = await api.get('/upload/schema-mappings')
      return data
    },
  })
}

export function useCreateSchemaMapping() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (mapping: Partial<SchemaMapping>) => {
      const { data } = await api.post('/upload/schema-mappings', mapping)
      return data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schema-mappings'] })
    },
  })
}
