// Endpoint Web Dashboard (lihat backend/apps/audits/views.py).
import { api } from './client'

export const getStats = (weeks = 8) =>
  api('/api/v1/admin/stats/', { params: { weeks } })

export const getDocuments = (params) =>
  api('/api/v1/admin/documents/', { params })

export const getDocument = (id) => api(`/api/v1/admin/documents/${id}/`)

export const reviewDocument = (id, body) =>
  api(`/api/v1/admin/documents/${id}/review/`, { method: 'PATCH', body })
