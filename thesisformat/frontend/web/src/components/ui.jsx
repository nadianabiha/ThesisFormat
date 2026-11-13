import { AlertCircle, Inbox } from 'lucide-react'
import { REVIEW_STATUS, documentType, scoreTone } from '../utils/constants'

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
  return (
    <span className="cell-sub" title={info.label}>
      <span className="type-dot" style={{ background: info.color }} />
      {info.label}
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
