// Endpoint Web Dashboard (lihat backend/apps/audits/views.py).
import { api } from './client'

export const getStats = (weeks = 8) =>
  api('/api/v1/admin/stats/', { params: { weeks } })

export const getDocuments = (params) =>
  api('/api/v1/admin/documents/', { params })

export const getDocument = (id) => api(`/api/v1/admin/documents/${id}/`)

export const getStudents = (search) =>
  api('/api/v1/admin/students/', { params: { search } })

// Tinjauan admin: { rejected_findings: [index...], review_note }
export const reviewDocument = (id, body) =>
  api(`/api/v1/admin/documents/${id}/review/`, { method: 'PATCH', body })

// Jalankan ulang Jalur A + Jalur B dengan aturan & instruksi AI terbaru.
export const reanalyzeDocument = (id) =>
  api(`/api/v1/admin/documents/${id}/reanalyze/`, { method: 'POST' })

// ---------- Pengawasan kualitas AI ----------

export const getAIPerformance = (days = 30) =>
  api('/api/v1/admin/ai-performance/', { params: { days } })

export const getRetestCandidates = (source, aspect, limit = 5) =>
  api('/api/v1/admin/ai-performance/retest-candidates/', {
    params: { source, aspect, limit },
  })

export const getRules = () => api('/api/v1/admin/rules/')

export const updateRule = (id, body) =>
  api(`/api/v1/admin/rules/${id}/`, { method: 'PATCH', body })
