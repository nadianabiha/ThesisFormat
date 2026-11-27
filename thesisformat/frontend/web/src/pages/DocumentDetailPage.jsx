import { useEffect, useMemo, useState } from 'react'
import { useParams } from 'react-router-dom'
import {
  AlertTriangle,
  BrainCircuit,
  Calendar,
  Check,
  CheckCircle2,
  RefreshCw,
  Ruler,
  User,
  X,
  XCircle,
} from 'lucide-react'
import { getDocument, reanalyzeDocument, reviewDocument } from '../api/dashboard'
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
import { COLORS, documentType, scoreLabel } from '../utils/constants'
import { formatDateTime } from '../utils/format'
import { useAsync } from '../utils/useAsync'

const FINDING_STYLE = {
  failed: { icon: X, tone: 'error', label: 'Gagal' },
  passed: { icon: Check, tone: 'success', label: 'Lulus' },
  pending: { icon: AlertTriangle, tone: 'warning', label: 'Belum dicek' },
}

const formatSeconds = (ms) => (ms ? `${(ms / 1000).toFixed(1)} detik` : '-')

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
          <span className="finding-title">{finding.aspect_label || finding.title}</span>
          <span className={`badge tone-${rejected ? 'info' : style.tone}`}>
            {rejected ? 'Ditandai keliru' : style.label}
          </span>
        </div>
        {finding.chapter && finding.chapter !== finding.location && (
          <div className="finding-loc">Bab: {finding.chapter}</div>
        )}
        {finding.location && <div className="finding-loc">{finding.location}</div>}
        {finding.detail && <div className="finding-detail">{finding.detail}</div>}
        {canReview && finding.status !== 'passed' && (
          <label className="reject-toggle">
            <input type="checkbox" checked={rejected} onChange={onToggle} />
            Temuan ini keliru (jadi umpan balik untuk memperbaiki AI)
          </label>
        )}
      </div>
    </div>
  )
}

/** Tinjauan admin: tandai temuan keliru + catatan. Skor dihitung ulang otomatis. */
function ReviewPanel({ doc, rejected, onSaved, onResetRejected }) {
  const review = doc.review
  const [note, setNote] = useState(review.note ?? '')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [saved, setSaved] = useState(false)

  useEffect(() => setNote(review.note ?? ''), [review])

  const savedRejected = doc.findings.filter((f) => f.rejected).map((f) => f.index)
  const currentRejected = [...rejected].sort((a, b) => a - b)
  const dirty =
    note !== (review.note ?? '') ||
    JSON.stringify(currentRejected) !== JSON.stringify(savedRejected)

  async function handleSave(event) {
    event.preventDefault()
    setSaving(true)
    setError(null)
    setSaved(false)
    try {
      onSaved(
        await reviewDocument(doc.id, {
          rejected_findings: currentRejected,
          review_note: note,
        }),
      )
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
          <h2>Tinjau hasil AI</h2>
          <p>Opsional. Hasil AI sudah langsung berlaku untuk mahasiswa.</p>
        </div>
      </div>

      <div className="alert alert-info-soft small">
        {/* Dibungkus satu <span> agar teks dan <strong> tidak dipecah jadi kolom oleh flex .alert */}
        <span>
          Centang temuan yang <strong>keliru</strong> pada daftar temuan. Temuan itu disembunyikan dari
          mahasiswa, skor <strong>dihitung ulang otomatis</strong>, dan tanda ini dipakai untuk mengamati
          pola kesalahan AI di halaman Kinerja AI.
        </span>
      </div>

      <div className="row small" style={{ justifyContent: 'space-between' }}>
        <span className="muted">
          {rejected.size > 0 ? `${rejected.size} temuan ditandai keliru` : 'Belum ada temuan yang ditandai'}
        </span>
        {JSON.stringify(currentRejected) !== JSON.stringify(savedRejected) && (
          <button type="button" className="btn btn-ghost btn-sm" onClick={onResetRejected}>
            Batalkan perubahan
          </button>
        )}
      </div>

      <div className="field">
        <label htmlFor="review_note">Catatan untuk mahasiswa (opsional)</label>
        <textarea
          id="review_note"
          className="textarea"
          maxLength={2000}
          placeholder="Mis. temuan abstrak keliru karena abstrak sudah sesuai panduan."
          value={note}
          onChange={(e) => setNote(e.target.value)}
        />
      </div>

      {review.corrected_score !== null && review.corrected_score !== undefined && (
        <div className="small">
          Skor dihitung ulang: <strong>{review.system_score}</strong> →{' '}
          <strong>{review.corrected_score}</strong> ({review.removed_findings} temuan keliru dihapus)
        </div>
      )}

      <ErrorAlert error={error} />
      {saved && !dirty && (
        <div className="alert alert-success" role="status">
          <Check size={18} /> Tinjauan tersimpan.
        </div>
      )}

      <button type="submit" className="btn btn-block" disabled={saving || !dirty}>
        {saving ? 'Menyimpan...' : dirty ? 'Simpan tinjauan' : 'Tidak ada perubahan'}
      </button>

      {review.reviewed_by && (
        <div className="small muted">
          Terakhir ditinjau oleh <strong>{review.reviewed_by.name}</strong>
          <br />
          {formatDateTime(review.reviewed_at)}
        </div>
      )}
    </form>
  )
}

/** Hasil perbandingan sebelum/sesudah analisis ulang. */
export function ComparisonResult({ comparison }) {
  const { before_score, after_score, ai_status, ai_error_label, feedback } = comparison
  return (
    <div className="stack small">
      <div className="row" style={{ justifyContent: 'space-between' }}>
        <span>
          Skor: <strong>{before_score ?? '-'}</strong> → <strong>{after_score ?? '-'}</strong>
        </span>
        <span className={`badge tone-${ai_status === 'success' ? 'success' : 'error'}`}>
          AI {ai_status === 'success' ? 'berhasil' : 'gagal'}
        </span>
      </div>
      {ai_status !== 'success' && ai_error_label && (
        <span className="muted">Penyebab: {ai_error_label}</span>
      )}
      {feedback.length > 0 && (
        <div className="stack" style={{ gap: 6 }}>
          <strong>Kesalahan yang dulu ditandai keliru:</strong>
          {feedback.map((item) => (
            <div key={`${item.source}-${item.aspect}`} className="row" style={{ flexWrap: 'nowrap' }}>
              {item.still_present === false ? (
                <CheckCircle2 size={16} color="var(--success)" />
              ) : item.still_present === true ? (
                <XCircle size={16} color="var(--error)" />
              ) : (
                <AlertTriangle size={16} color="var(--warning-strong)" />
              )}
              <span>
                {item.label}:{' '}
                {item.still_present === false
                  ? 'tidak muncul lagi'
                  : item.still_present === true
                    ? 'masih muncul'
                    : 'belum bisa dinilai (AI gagal)'}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

/** Status analisis AI terakhir + tombol analisis ulang. */
function AIPanel({ doc, onReanalyzed }) {
  const ai = doc.ai
  const [confirming, setConfirming] = useState(false)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState(null)
  const [comparison, setComparison] = useState(null)

  async function run() {
    setConfirming(false)
    setRunning(true)
    setError(null)
    setComparison(null)
    try {
      const result = await reanalyzeDocument(doc.id)
      setComparison(result.comparison)
      onReanalyzed(result.document)
    } catch (err) {
      setError(err)
    } finally {
      setRunning(false)
    }
  }

  return (
    <section className="card stack">
      <div className="card-title" style={{ marginBottom: 0 }}>
        <div>
          <h2>Analisis AI</h2>
          <p>Status analisis Gemini terakhir untuk dokumen ini.</p>
        </div>
      </div>

      {ai ? (
        <div className="stack small" style={{ gap: 6 }}>
          <div className="row" style={{ justifyContent: 'space-between' }}>
            <span className="muted">Status</span>
            <span className={`badge tone-${ai.status === 'success' ? 'success' : 'error'}`}>
              {ai.status === 'success' ? 'Berhasil' : 'Gagal'}
            </span>
          </div>
          {ai.status !== 'success' && (
            <div className="row" style={{ justifyContent: 'space-between' }}>
              <span className="muted">Penyebab</span>
              <span>{ai.error_label || 'Tidak diketahui'}</span>
            </div>
          )}
          <div className="row" style={{ justifyContent: 'space-between' }}>
            <span className="muted">Model</span>
            <span>{ai.model || '-'}</span>
          </div>
          <div className="row" style={{ justifyContent: 'space-between' }}>
            <span className="muted">Waktu proses</span>
            <span>{formatSeconds(ai.duration_ms)}</span>
          </div>
          <div className="row" style={{ justifyContent: 'space-between' }}>
            <span className="muted">Versi aturan</span>
            <span>v{ai.rule_version}</span>
          </div>
          <div className="row" style={{ justifyContent: 'space-between' }}>
            <span className="muted">Waktu analisis</span>
            <span>{formatDateTime(ai.created_at)}</span>
          </div>
          {ai.unknown_categories?.length > 0 && (
            <div className="alert alert-warning small">
              <AlertTriangle size={16} />
              <div>
                AI memakai kategori yang tidak dikenali: {ai.unknown_categories.join(', ')}
              </div>
            </div>
          )}
        </div>
      ) : (
        <p className="muted small" style={{ margin: 0 }}>
          Belum ada catatan analisis AI untuk dokumen ini.
        </p>
      )}

      <ErrorAlert error={error} />

      {comparison && (
        <div className="alert alert-success" role="status" style={{ display: 'block' }}>
          <strong style={{ display: 'block', marginBottom: 8 }}>Hasil analisis ulang</strong>
          <ComparisonResult comparison={comparison} />
        </div>
      )}

      {doc.can_reanalyze &&
        (running ? (
          <div className="alert alert-info-soft small" role="status">
            <RefreshCw size={16} className="spin" />
            Menganalisis ulang dengan aturan terbaru… bisa sampai 2 menit.
          </div>
        ) : confirming ? (
          <div className="stack" style={{ gap: 8 }}>
            <span className="small">
              Jalankan ulang pemeriksaan format &amp; AI dengan aturan terbaru? Tanda keliru pada
              temuan saat ini akan direset (riwayatnya tetap tersimpan).
            </span>
            <div className="row">
              <button type="button" className="btn btn-sm" onClick={run}>
                Ya, analisis ulang
              </button>
              <button type="button" className="btn btn-ghost btn-sm" onClick={() => setConfirming(false)}>
                Batal
              </button>
            </div>
          </div>
        ) : (
          <button type="button" className="btn btn-ghost btn-block" onClick={() => setConfirming(true)}>
            <RefreshCw size={16} /> Analisis ulang AI
          </button>
        ))}
    </section>
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
  const recalculated =
    doc.review?.corrected_score !== null && doc.review?.corrected_score !== undefined

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
              {/* AI gagal: nilai tersimpan hanya nilai format, jadi belum ada nilai akhir. */}
              <ScoreRing score={doc.has_semantic_score ? doc.score : null} size={112} stroke={10} light caption="/100" />
              <div style={{ flex: 1, minWidth: 220 }}>
                <div className="row" style={{ marginBottom: 8 }}>
                  <span className="badge" style={{ background: 'rgba(255,255,255,.2)', color: '#fff' }}>
                    <TypeIcon size={13} /> {type.label}
                  </span>
                  <span className="badge" style={{ background: '#fff', color: 'var(--hero-end)' }}>
                    {doc.has_semantic_score ? scoreLabel(doc.score) : 'Belum lengkap: analisis AI gagal'}
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
                </div>
                {recalculated && (
                  <div className="small" style={{ marginTop: 10, opacity: 0.9 }}>
                    Skor dihitung ulang setelah {doc.review.removed_findings} temuan ditandai keliru:{' '}
                    {doc.review.system_score} → {doc.review.corrected_score}
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
                <strong>Analisis AI gagal untuk dokumen ini.</strong> Gunakan tombol{' '}
                <em>Analisis ulang AI</em> di panel kanan untuk mencobanya lagi.
                <br />
                <span className="small">{doc.ai_error}</span>
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
                  {physical.length ? (
                    renderFindings(physical)
                  ) : (
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
                  {semantic.length ? (
                    renderFindings(semantic)
                  ) : (
                    <p className="muted small">
                      {doc.has_semantic_score
                        ? 'Tidak ada temuan dari AI.'
                        : 'Belum ada hasil dari AI karena analisis AI gagal.'}
                    </p>
                  )}
                </div>
              </section>
            </>
          )}
        </div>

        <aside className="review-panel">
          <AIPanel doc={doc} onReanalyzed={setData} />
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
                <h2>Tinjau hasil AI</h2>
              </div>
              <p className="muted small" style={{ margin: 0 }}>
                Dokumen ini belum memiliki hasil pemeriksaan tersimpan. Jalankan{' '}
                <em>Analisis ulang AI</em> terlebih dahulu.
              </p>
            </section>
          )}
          <section className="card">
            <div className="row" style={{ justifyContent: 'space-between' }}>
              <span className="muted small">Status tinjauan</span>
              <ReviewBadge status={doc.review_status} />
            </div>
          </section>
        </aside>
      </div>
    </>
  )
}
