import {
  AlertCircle,
  Briefcase,
  Check,
  FileCheck2,
  FileText,
  FlaskConical,
  GraduationCap,
  HeartHandshake,
  Inbox,
  Lightbulb,
  Newspaper,
} from 'lucide-react'
import { REVIEW_STATUS, documentType, scoreTone } from '../utils/constants'

// Ikon per jenis dokumen (padanan DocTypeStyle di app mobile).
const TYPE_ICONS = {
  praktik: FlaskConical,
  pkl: Briefcase,
  tugas_akhir: GraduationCap,
  proposal_pengabdian: HeartHandshake,
  proposal_penelitian: Lightbulb,
  makalah_ilmiah: Newspaper,
}

export function typeIcon(id) {
  return TYPE_ICONS[id] ?? FileText
}

/** Kotak ikon berwarna sesuai jenis dokumen. */
export function DocTypeIcon({ type, size = 44 }) {
  const info = documentType(type)
  const Icon = typeIcon(type)
  return (
    <span
      className="doc-type-icon"
      style={{
        width: size,
        height: size,
        borderRadius: size * 0.32,
        background: `${info.color}1f`,
        color: info.color,
      }}
      aria-hidden="true"
    >
      <Icon size={size * 0.5} />
    </span>
  )
}

/** Chip pil (filter), sama seperti PillChip di app mobile. */
export function PillChip({ label, selected, onClick, icon: Icon, color }) {
  const accent = color ?? 'var(--primary)'
  return (
    <button
      type="button"
      className={`pill-chip${selected ? ' selected' : ''}`}
      style={selected ? { background: accent, borderColor: accent } : undefined}
      aria-pressed={selected}
      onClick={onClick}
    >
      {Icon && (
        <span
          className="pill-chip-icon"
          style={{
            background: selected ? 'rgba(255,255,255,.25)' : `${color ?? '#0B3B5B'}1f`,
            color: selected ? '#fff' : accent,
          }}
        >
          <Icon size={13} />
        </span>
      )}
      {label}
    </button>
  )
}

/**
 * Ilustrasi sederhana: gumpalan warna, kertas dokumen, lencana.
 * Padanan BlobIllustration di app mobile (tanpa aset gambar).
 */
export function BlobIllustration({
  size = 160,
  icon: Icon = FileCheck2,
  badge: Badge = Check,
  blob = 'var(--primary-light)',
  badgeColor = 'var(--accent)',
}) {
  const s = size
  const line = (width) => (
    <span className="blob-line" style={{ width: s * width, height: s * 0.032 }} />
  )
  return (
    <div className="blob-illus" style={{ width: s, height: s }} aria-hidden="true">
      <span
        className="blob-shape"
        style={{
          left: s * 0.06,
          top: s * 0.08,
          width: s * 0.88,
          height: s * 0.84,
          background: blob,
          borderRadius: `${s * 0.5}px ${s * 0.36}px ${s * 0.5}px ${s * 0.34}px`,
        }}
      />
      <span
        className="blob-dot"
        style={{ right: s * 0.02, top: s * 0.04, width: s * 0.09, height: s * 0.09, background: 'var(--accent)' }}
      />
      <span
        className="blob-dot"
        style={{ left: 0, bottom: s * 0.18, width: s * 0.06, height: s * 0.06, background: 'rgba(69,211,216,.6)' }}
      />
      <span
        className="blob-paper"
        style={{
          left: s * 0.27,
          top: s * 0.19,
          width: s * 0.46,
          height: s * 0.58,
          padding: s * 0.055,
          borderRadius: s * 0.07,
          gap: s * 0.03,
        }}
      >
        <Icon size={s * 0.13} color="var(--primary)" />
        <span style={{ height: s * 0.01 }} />
        {line(0.33)}
        {line(0.26)}
        {line(0.31)}
        {line(0.18)}
      </span>
      <span
        className="blob-badge"
        style={{
          right: s * 0.12,
          bottom: s * 0.13,
          width: s * 0.21,
          height: s * 0.21,
          background: badgeColor,
        }}
      >
        <Badge size={s * 0.11} color="#fff" />
      </span>
    </div>
  )
}

const TONE_COLOR = {
  success: 'var(--success)',
  primary: 'var(--primary)',
  warning: 'var(--warning-strong)',
  muted: 'var(--text-muted)',
}

export function Spinner() {
  return <div className="spinner" role="status" aria-label="Memuat" />
}

export function ErrorAlert({ error, onRetry }) {
  if (!error) return null
  return (
    <div className="alert alert-error" role="alert">
      <AlertCircle size={18} />
      <div style={{ flex: 1 }}>{error.message || String(error)}</div>
      {onRetry && (
        <button type="button" className="btn btn-ghost btn-sm" onClick={onRetry}>
          Coba lagi
        </button>
      )}
    </div>
  )
}

export function EmptyState({ icon: Icon = Inbox, title, children }) {
  return (
    <div className="empty">
      <div className="empty-icon">
        <Icon size={24} />
      </div>
      {title && <strong style={{ color: 'var(--text)' }}>{title}</strong>}
      {children && <div className="small" style={{ marginTop: 4 }}>{children}</div>}
    </div>
  )
}

export function TypeBadge({ type }) {
  const info = documentType(type)
  const Icon = typeIcon(type)
  return (
    <span
      className="type-badge"
      title={info.label}
      style={{ background: `${info.color}1a`, color: info.color }}
    >
      <Icon size={12} />
      {info.short}
    </span>
  )
}

export function ReviewBadge({ status }) {
  if (!status) return <span className="badge tone-muted">Belum ada hasil</span>
  const info = REVIEW_STATUS[status] ?? { label: status, tone: 'muted' }
  return <span className={`badge tone-${info.tone}`}>{info.label}</span>
}

/** Cincin skor 0-100 (SVG). */
export function ScoreRing({ score, size = 56, stroke = 6, light = false, caption }) {
  const radius = (size - stroke) / 2
  const circumference = 2 * Math.PI * radius
  const value = score === null || score === undefined ? null : Math.max(0, Math.min(100, score))
  const color = light ? '#fff' : TONE_COLOR[scoreTone(value)]
  const track = light ? 'rgba(255,255,255,0.25)' : 'var(--surface-2)'

  return (
    <div
      className="score-ring"
      style={{ width: size, height: size }}
      role="img"
      aria-label={value === null ? 'Belum ada skor' : `Skor ${value} dari 100`}
    >
      <svg width={size} height={size}>
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke={track} strokeWidth={stroke} />
        {value !== null && (
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={circumference * (1 - value / 100)}
          />
        )}
      </svg>
      <div
        className="value"
        style={{ fontSize: size * 0.3, color: light ? '#fff' : 'var(--text)' }}
      >
        {value === null ? '–' : value}
        {caption && <small>{caption}</small>}
      </div>
    </div>
  )
}
