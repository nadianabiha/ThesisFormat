import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  AlertTriangle,
  BrainCircuit,
  Calendar,
  Check,
  Download,
  Ruler,
  User,
  X,
} from 'lucide-react'
import { getDocument, reviewDocument } from '../api/dashboard'
import PageNav from '../components/PageNav'
import {
  BlobIllustration,
  EmptyState,
  ErrorAlert,
  ReviewBadge,
  ScoreRing,
  Spinner,
  typeIcon,
} from '../components/ui'
import { COLORS, REVIEW_STATUS, documentType, scoreLabel } from '../utils/constants'
import { formatDateTime } from '../utils/format'
import { useAsync } from '../utils/useAsync'

const FINDING_STYLE = {
  failed: { icon: X, tone: 'error', label: 'Gagal' },
  passed: { icon: Check, tone: 'success', label: 'Lulus' },
  pending: { icon: AlertTriangle, tone: 'warning', label: 'Belum dicek' },
}

function ScoreTile({ icon: Icon, color, title, weight, score, available }) {
  return (
    <div className="card score-tile">
      <div className="row" style={{ justifyContent: 'space-between' }}>
        <span className="stat-icon" style={{ background: `${color}1f`, color }}>
          <Icon size={20} />
        </span>
        <span className="small muted">Bobot {weight}</span>
      </div>
      <div className="stat-label" style={{ marginTop: 12 }}>
        {title}
      </div>
      <div className="stat-value">
        {available ? score : '–'}
        {available && <span className="small muted"> /100</span>}
      </div>
      {available ? (
        <div className="bar">
          <span style={{ width: `${score}%`, background: color }} />
        </div>
      ) : (
        <div className="small muted" style={{ marginTop: 10 }}>
          Skor belum tersedia
        </div>
      )}
    </div>
  )
}

function FindingItem({ finding, canReview, rejected, onToggle }) {
  const style = FINDING_STYLE[finding.status] ?? FINDING_STYLE.pending
  const Icon = style.icon
  return (
    <div className={`finding${rejected ? ' rejected' : ''}`}>
      <div className={`finding-icon tone-${style.tone}`}>
        <Icon size={18} />
      </div>
      <div className="finding-body">
        <div className="finding-head">
          <span className="finding-title">{finding.title}</span>
          <span className={`badge tone-${rejected ? 'muted' : style.tone}`}>
            {rejected ? 'Ditolak admin' : style.label}
          </span>
        </div>
        {finding.location && <div className="finding-loc">{finding.location}</div>}
        {finding.detail && <div className="finding-detail">{finding.detail}</div>}
        {canReview && finding.status !== 'passed' && (
          <label className="reject-toggle">
            <input type="checkbox" checked={rejected} onChange={onToggle} />
            Tandai temuan ini keliru (tidak ditampilkan ke mahasiswa)
          </label>
        )}
      </div>
    </div>
  )
}

function ReviewPanel({ doc, rejected, onSaved, onResetRejected }) {
  const review = doc.review
  const [status, setStatus] = useState(review.status)
  const [score, setScore] = useState(review.corrected_score ?? review.system_score)
  const [note, setNote] = useState(review.note ?? '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    setStatus(review.status)
    setScore(review.corrected_score ?? review.system_score)
    setNote(review.note ?? '')
  }, [review])

  const savedRejected = doc.findings.filter((f) => f.rejected).map((f) => f.index)
  const dirty =
    status !== review.status ||
    note !== (review.note ?? '') ||
    (status === 'corrected' && Number(score) !== review.corrected_score) ||
    JSON.stringify([...rejected].sort((a, b) => a - b)) !== JSON.stringify(savedRejected)

  const scoreInvalid =
    status === 'corrected' &&
    (score === '' || Number.isNaN(Number(score)) || Number(score) < 0 || Number(score) > 100)

  async function handleSave(event) {
    event.preventDefault()
    if (scoreInvalid) return
    setSaving(true)
    setError(null)
    setSaved(false)
    try {
      const updated = await reviewDocument(doc.id, {
        review_status: status,
        corrected_score: status === 'corrected' ? Math.round(Number(score)) : null,
        review_note: note,
        rejected_findings: [...rejected],
      })
      onSaved(updated)
      setSaved(true)
    } catch (err) {
      setError(err)
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="card stack" onSubmit={handleSave}>
      <div className="card-title" style={{ marginBottom: 0 }}>
        <div>
          <h2>Review hasil AI</h2>
          <p>Validasi atau koreksi sebelum hasil dipakai mahasiswa.</p>
        </div>
      </div>

      <fieldset style={{ border: 0, padding: 0, margin: 0 }}>
        <legend className="small" style={{ fontWeight: 600, marginBottom: 8 }}>
          Status
        </legend>
        <div className="segmented" role="radiogroup">
          {Object.entries(REVIEW_STATUS).map(([value, info]) => (
            <label key={value} className={status === value ? 'checked' : ''}>
              <input
                type="radio"
                name="review_status"
                value={value}
                checked={status === value}
                onChange={() => setStatus(value)}
              />
              {info.label}
            </label>
          ))}
        </div>
      </fieldset>

      {status === 'corrected' && (
        <div className="field">
          <label htmlFor="corrected_score">Skor koreksi (0–100)</label>
          <input
            id="corrected_score"
            type="number"
            min={0}
            max={100}
            className="input"
            value={score}
            onChange={(e) => setScore(e.target.value)}
            aria-invalid={scoreInvalid}
          />
          <span className="small muted">Skor sistem: {review.system_score}</span>
          {scoreInvalid && (
            <span className="small" style={{ color: 'var(--error)' }}>
              Isi angka antara 0 dan 100.
            </span>
          )}
        </div>
      )}

      <div className="field">
        <label htmlFor="review_note">Catatan untuk mahasiswa (opsional)</label>
        <textarea
          id="review_note"
          className="textarea"
          maxLength={2000}
          placeholder="Mis. temuan abstrak keliru karena…"
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
      </div>

      <div className="small muted">
        {rejected.size > 0
          ? `${rejected.size} temuan ditandai keliru.`
          : 'Tandai temuan yang keliru pada daftar temuan.'}
        {rejected.size > 0 && (
          <>
            {' '}
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              style={{ marginLeft: 4 }}
              onClick={onResetRejected}
            >
              Batalkan tanda
            </button>
          </>
        )}
      </div>

      <ErrorAlert error={error} />
      {saved && !dirty && (
        <div className="alert alert-success" role="status">
          <Check size={18} /> Review tersimpan.
        </div>
      )}

      <button type="submit" className="btn btn-block" disabled={saving || !dirty || scoreInvalid}>
        {saving ? 'Menyimpan...' : dirty ? 'Simpan review' : 'Tidak ada perubahan'}
      </button>

      {review.reviewed_by && (
        <div className="small muted">
          Terakhir direview oleh <strong>{review.reviewed_by.name}</strong>
          <br />
          {formatDateTime(review.reviewed_at)}
        </div>
      )}
    </form>
  )
}

export default function DocumentDetailPage() {
  const { id } = useParams()
  const { data: doc, loading, error, reload, setData } = useAsync(() => getDocument(id), [id])
  const [rejected, setRejected] = useState(new Set())

  const initialRejected = useMemo(
    () => new Set((doc?.findings ?? []).filter((f) => f.rejected).map((f) => f.index)),
    [doc],
  )
  useEffect(() => setRejected(new Set(initialRejected)), [initialRejected])

  // Tombol Kembali membuka daftar dokumen asal (lengkap dengan filternya,
  // dikirim lewat location.state.from oleh halaman Dokumen).
  const backNav = <PageNav label="daftar dokumen" fallback="/documents" />

  if (loading && !doc) return <Spinner />
  if (error && !doc) {
    return (
      <>
        {backNav}
        <ErrorAlert error={error} onRetry={error.status === 404 ? undefined : reload} />
      </>
    )
  }

  const type = documentType(doc.document_type)
  const TypeIcon = typeIcon(doc.document_type)
  const physical = doc.findings.filter((f) => f.source !== 'semantic')
  const semantic = doc.findings.filter((f) => f.source === 'semantic')
  const corrected = doc.review?.corrected_score !== null && doc.review?.corrected_score !== undefined

  function toggle(index) {
    setRejected((prev) => {
      const next = new Set(prev)
      if (next.has(index)) next.delete(index)
      else next.add(index)
      return next
    })
  }

  const renderFindings = (items) =>
    items.map((finding) => (
      <FindingItem
        key={finding.index}
        finding={finding}
        canReview={doc.can_review}
        rejected={rejected.has(finding.index)}
        onToggle={() => toggle(finding.index)}
      />
    ))

  return (
    <>
      {backNav}

      <div className="detail-grid">
        <div className="detail-main">
          <section className="hero-card">
            <div className="hero-row">
              <ScoreRing score={doc.score} size={112} stroke={10} light caption="/100" />
              <div style={{ flex: 1, minWidth: 220 }}>
                <div className="row" style={{ marginBottom: 8 }}>
                  <span className="badge" style={{ background: 'rgba(255,255,255,.2)', color: '#fff' }}>
                    <TypeIcon size={13} /> {type.label}
                  </span>
                  <span className="badge" style={{ background: '#fff', color: 'var(--hero-end)' }}>
                    {scoreLabel(doc.score)}
                  </span>
                </div>
                <h1>{doc.title}</h1>
                <div className="hero-meta">
                  <span>
                    <User size={14} /> {doc.student.name} ({doc.student.email})
                  </span>
                  <span>
                    <Calendar size={14} /> {formatDateTime(doc.uploaded_at)}
                  </span>
                  {doc.file_url && (
                    <a href={doc.file_url} target="_blank" rel="noreferrer">
                      <Download size={14} style={{ verticalAlign: '-2px' }} /> Buka file
                    </a>
                  )}
                </div>
                {corrected && (
                  <div className="small" style={{ marginTop: 10, opacity: 0.9 }}>
                    Skor dikoreksi admin: {doc.review.system_score} → {doc.review.corrected_score}
                  </div>
                )}
              </div>
              <div className="hero-illus">
                <BlobIllustration size={130} blob="rgba(255,255,255,.22)" icon={TypeIcon} />
              </div>
            </div>
          </section>

          <div className="score-tiles">
            <ScoreTile
              icon={Ruler}
              color={COLORS.primary}
              title="Format dokumen (Jalur A)"
              weight="40%"
              score={doc.format_score}
              available={doc.has_result}
            />
            <ScoreTile
              icon={BrainCircuit}
              color={COLORS.accent}
              title="Struktur & isi oleh AI (Jalur B)"
              weight="60%"
              score={doc.semantic_score}
              available={doc.has_semantic_score}
            />
          </div>

          {doc.ai_error && !doc.has_semantic_score && (
            <div className="alert alert-warning">
              <AlertTriangle size={18} />
              <div>
                <strong>Analisis AI gagal untuk dokumen ini.</strong>
                <br />
                {doc.ai_error}
              </div>
            </div>
          )}

          {!doc.has_result ? (
            <section className="card">
              <EmptyState title="Belum ada hasil pemeriksaan">
                Dokumen ini belum diproses atau pemeriksaannya gagal.
              </EmptyState>
            </section>
          ) : (
            <>
              <section className="card">
                <div className="card-title">
                  <div>
                    <h2>Aspek format ({physical.length})</h2>
                    <p>Font, ukuran, spasi, perataan, dan margin.</p>
                  </div>
                </div>
                <div className="findings">
                  {physical.length ? renderFindings(physical) : (
                    <p className="muted small">Tidak ada temuan format.</p>
                  )}
                </div>
              </section>

              <section className="card">
                <div className="card-title">
                  <div>
                    <h2>Aspek isi oleh AI ({semantic.length})</h2>
                    <p>Sitasi, daftar isi, hierarki bab, abstrak, bahasa, dan konsistensi.</p>
                  </div>
                </div>
                <div className="findings">
                  {semantic.length ? renderFindings(semantic) : (
                    <p className="muted small">Tidak ada temuan dari AI.</p>
                  )}
                </div>
              </section>
            </>
          )}
        </div>

        <aside className="review-panel">
          {doc.can_review ? (
            <ReviewPanel
              doc={doc}
              rejected={rejected}
              onSaved={setData}
              onResetRejected={() => setRejected(new Set(initialRejected))}
            />
          ) : (
            <section className="card">
              <div className="card-title">
                <h2>Review hasil AI</h2>
              </div>
              <p className="muted small" style={{ margin: 0 }}>
                Dokumen ini belum memiliki hasil pemeriksaan tersimpan, sehingga belum bisa direview.
              </p>
            </section>
          )}
          <section className="card">
            <div className="row" style={{ justifyContent: 'space-between' }}>
              <span className="muted small">Status review</span>
              <ReviewBadge status={doc.review_status} />
            </div>
          </section>
        </aside>
      </div>
    </>
  )
}
