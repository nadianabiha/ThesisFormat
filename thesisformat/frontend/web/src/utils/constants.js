// Disamakan dengan backend (Document.DocumentType) dan app mobile
// (lib/models/document_type.dart + DocTypeStyle).
export const DOCUMENT_TYPES = [
  { id: 'praktik', label: 'Laporan Praktik', color: '#1E88D6' },
  { id: 'pkl', label: 'Laporan PKL/Magang', color: '#F59E1B' },
  { id: 'tugas_akhir', label: 'Laporan Tugas Akhir/Skripsi', color: '#7C6CF2' },
  { id: 'proposal_pengabdian', label: 'Proposal Pengabdian Masyarakat', color: '#1FA874' },
  { id: 'proposal_penelitian', label: 'Proposal Penelitian', color: '#0F9F8F' },
  { id: 'makalah_ilmiah', label: 'Makalah Ilmiah', color: '#DB2777' },
]

export function documentType(id) {
  return (
    DOCUMENT_TYPES.find((type) => type.id === id) ?? {
      id,
      label: id || 'Tidak diketahui',
      color: '#66778A',
    }
  )
}

export const REVIEW_STATUS = {
  pending: { label: 'Menunggu review', tone: 'warning' },
  validated: { label: 'Tervalidasi', tone: 'success' },
  corrected: { label: 'Dikoreksi', tone: 'info' },
}

// Skor minimal "memenuhi standar" (sama dengan backend PASSING_SCORE).
export const PASSING_SCORE = 75

export function scoreTone(score) {
  if (score === null || score === undefined) return 'muted'
  if (score >= 90) return 'success'
  if (score >= PASSING_SCORE) return 'primary'
  return 'warning'
}

export function scoreLabel(score) {
  if (score === null || score === undefined) return 'Belum ada skor'
  if (score >= 90) return 'Sangat baik'
  if (score >= PASSING_SCORE) return 'Memenuhi standar'
  return 'Perlu perbaikan'
}

export const COLORS = {
  primary: '#1E88D6',
  primarySoft: '#CDEBFC',
  accent: '#F59E1B',
  success: '#1FA874',
  error: '#E5484D',
  info: '#7C6CF2',
  muted: '#9DABBA',
  grid: '#EDF3F8',
  text: '#66778A',
}
