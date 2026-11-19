import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Tooltip,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  Flag,
  FlaskConical,
  RefreshCw,
  SlidersHorizontal,
  X,
  XCircle,
} from 'lucide-react'
import { getAIPerformance, getRetestCandidates, reanalyzeDocument } from '../api/dashboard'
import PageNav from '../components/PageNav'
import { EmptyState, ErrorAlert, Spinner } from '../components/ui'
import { COLORS } from '../utils/constants'
import { formatDateTime, formatNumber } from '../utils/format'
import { useAsync } from '../utils/useAsync'

ChartJS.register(BarElement, CategoryScale, Legend, LinearScale, Tooltip)

const SOURCE_LABEL = { semantic: 'Isi (AI)', physical: 'Format' }

function Stat({ icon: Icon, color, label, value, hint }) {
  return (
    <div className="card stat-card" style={{ '--stat-color': color, '--stat-shadow': `${color}55` }}>
      <div className="stat-top">
        <span className="stat-label">{label}</span>
        <span className="stat-icon solid" style={{ background: `linear-gradient(135deg, ${color}cc, ${color})` }}>
          <Icon size={19} />
        </span>
      </div>
      <div className="stat-value">{value}</div>
      {hint && <div className="stat-hint">{hint}</div>}
    </div>
  )
}

/**
 * Uji ulang: jalankan ulang AI pada dokumen yang dulu ditandai keliru
 * untuk satu aspek, lalu hitung berapa yang kesalahannya hilang.
 */
function RetestPanel({ aspect, onClose, onDone }) {
  const { data, loading, error } = useAsync(
    () => getRetestCandidates(aspect.source, aspect.aspect, 5),
    [aspect.source, aspect.aspect],
  )
  const [results, setResults] = useState({})
  const [running, setRunning] = useState(false)

  const candidates = data?.results ?? []
  const finished = candidates.length > 0 && candidates.every((c) => results[c.document_id])

  async function start() {
    setRunning(true)
    setResults({})
    // Satu per satu agar setiap permintaan tidak terlalu lama dan progres terlihat.
    for (const candidate of candidates) {
      setResults((prev) => ({ ...prev, [candidate.document_id]: { state: 'running' } }))
      try {
        const { comparison } = await reanalyzeDocument(candidate.document_id)
        const item = comparison.feedback.find(
          (f) => f.source === aspect.source && f.aspect === aspect.aspect,
        )
        setResults((prev) => ({
          ...prev,
          [candidate.document_id]: {
            state: 'done',
            stillPresent: item ? item.still_present : null,
            before: comparison.before_score,
            after: comparison.after_score,
            aiError: comparison.ai_status !== 'success' ? comparison.ai_error_label : '',
          },
        }))
      } catch (err) {
        setResults((prev) => ({
          ...prev,
          [candidate.document_id]: { state: 'error', message: err.message },
        }))
      }
    }
    setRunning(false)
    onDone()
  }

  const values = Object.values(results)
  const resolved = values.filter((r) => r.stillPresent === false).length
  const still = values.filter((r) => r.stillPresent === true).length

  return (
    <section className="card retest-panel" aria-live="polite">
      <div className="card-title">
        <div>
          <h2>
            Uji ulang: {aspect.label}{' '}
            <span className="small muted">({SOURCE_LABEL[aspect.source]})</span>
          </h2>
          <p>
            Jalankan ulang pemeriksaan dengan aturan & instruksi AI terbaru pada dokumen yang dulu
            ditandai keliru di aspek ini.
          </p>
        </div>
        <button type="button" className="icon-btn" aria-label="Tutup" onClick={onClose} disabled={running}>
          <X size={18} />
        </button>
      </div>

      <ErrorAlert error={error} />
      {loading ? (
        <Spinner />
      ) : candidates.length === 0 ? (
        <EmptyState icon={FlaskConical} title="Belum ada dokumen untuk diuji">
          Tandai temuan yang keliru pada aspek ini di halaman detail dokumen terlebih dahulu.
        </EmptyState>
      ) : (
        <div className="stack">
          <div className="retest-list">
            {candidates.map((candidate) => {
              const result = results[candidate.document_id]
              return (
                <div key={candidate.document_id} className="retest-row">
                  <Link to={`/documents/${candidate.document_id}`} state={{ from: '/ai-performance' }} className="cell-title">
                    {candidate.title}
                  </Link>
                  <span className="small">
                    {!result && <span className="muted">Menunggu</span>}
                    {result?.state === 'running' && (
                      <span className="row muted">
                        <RefreshCw size={14} className="spin" /> Menganalisis…
                      </span>
                    )}
                    {result?.state === 'error' && <span style={{ color: 'var(--error)' }}>Gagal: {result.message}</span>}
                    {result?.state === 'done' && (
                      <span className="row">
                        {result.stillPresent === false && (
                          <>
                            <CheckCircle2 size={15} color="var(--success)" /> Kesalahan hilang
                          </>
                        )}
                        {result.stillPresent === true && (
                          <>
                            <XCircle size={15} color="var(--error)" /> Masih muncul
                          </>
                        )}
                        {result.stillPresent === null && (
                          <>
                            <AlertTriangle size={15} color="var(--warning-strong)" />{' '}
                            {result.aiError ? `AI gagal (${result.aiError})` : 'Tidak bisa dinilai'}
                          </>
                        )}
                        <span className="muted">
                          · skor {result.before ?? '-'} → {result.after ?? '-'}
                        </span>
                      </span>
                    )}
                  </span>
                </div>
              )
            })}
          </div>

          {finished && (
            <div className={`alert ${resolved > 0 ? 'alert-success' : 'alert-warning'}`} role="status">
              <Activity size={18} />
              <div>
                <strong>
                  Kesalahan hilang di {resolved} dari {candidates.length} dokumen
                </strong>
                {still > 0 && ` · masih muncul di ${still} dokumen`}
                <br />
                {resolved > 0
                  ? 'Perbaikan aturan berdampak. Pantau terus pada unggahan berikutnya.'
                  : 'Belum berdampak. Coba perjelas instruksi AI untuk aspek ini.'}
              </div>
            </div>
          )}

          <div className="row">
            <button type="button" className="btn" onClick={start} disabled={running}>
              <FlaskConical size={16} />
              {running ? 'Menguji…' : finished ? 'Uji lagi' : `Mulai uji ulang (${candidates.length} dokumen)`}
            </button>
            <span className="small muted">Setiap dokumen bisa memakan waktu hingga 2 menit.</span>
          </div>
        </div>
      )}
    </section>
  )
}

export default function AIPerformancePage() {
  const [days, setDays] = useState(30)
  const { data, loading, error, reload } = useAsync(() => getAIPerformance(days), [days])
  const [retestAspect, setRetestAspect] = useState(null)

  if (!data && loading) return <Spinner />
  if (!data && error) return <ErrorAlert error={error} onRetry={reload} />

  const { runs, aspects, recent_feedback: recent, versions } = data
  const recentRuns = data.recent_runs ?? []
  const problemAspects = aspects.filter((a) => a.feedback_count > 0)

  return (
    <>
      <PageNav label="Ringkasan" fallback="/" />

      <div className="page-header">
        <div>
          <h1>Kinerja AI</h1>
          <p>
            Amati apakah AI bekerja optimal, temukan pola kesalahannya, lalu perbaiki aturan dan uji
            ulang hasilnya.
          </p>
        </div>
        <div className="field" style={{ minWidth: 180 }}>
          <label htmlFor="days" className="small muted">
            Periode
          </label>
          <select id="days" className="select" value={days} onChange={(e) => setDays(Number(e.target.value))}>
            <option value={7}>7 hari terakhir</option>
            <option value={30}>30 hari terakhir</option>
            <option value={90}>90 hari terakhir</option>
            <option value={365}>1 tahun terakhir</option>
          </select>
        </div>
      </div>

      {error && (
        <div style={{ marginBottom: 16 }}>
          <ErrorAlert error={error} onRetry={reload} />
        </div>
      )}

      <div className="cycle-steps" aria-label="Siklus perbaikan AI">
        {[
          ['1', 'Amati', 'Kegagalan & temuan keliru tercatat otomatis'],
          ['2', 'Temukan pola', 'Aspek mana yang paling sering keliru'],
          ['3', 'Perbaiki', 'Ubah aturan atau instruksi AI'],
          ['4', 'Uji ulang', 'Buktikan kesalahannya berkurang'],
        ].map(([number, title, text]) => (
          <div key={number} className="cycle-step">
            <span className="cycle-number">{number}</span>
            <div>
              <strong>{title}</strong>
              <div className="small muted">{text}</div>
            </div>
          </div>
        ))}
      </div>

      <div className="stat-grid">
        <Stat
          icon={Activity}
          color={COLORS.primary}
          label="Analisis AI"
          value={formatNumber(runs.total)}
          hint={`${runs.success} berhasil · ${runs.failed} gagal`}
        />
        <Stat
          icon={CheckCircle2}
          color={COLORS.success}
          label="Tingkat keberhasilan"
          value={formatNumber(runs.success_rate, '%')}
          hint={`Aturan saat ini: versi ${data.current_rule_version}`}
        />
        <Stat
          icon={Clock}
          color={COLORS.accent}
          label="Rata-rata waktu AI"
          value={runs.avg_duration_ms ? `${(runs.avg_duration_ms / 1000).toFixed(1)} dtk` : '-'}
          hint={runs.by_model[0] ? `Paling sering: ${runs.by_model[0].model}` : 'Belum ada data model'}
        />
        <Stat
          icon={Flag}
          color={COLORS.error}
          label="Temuan ditandai keliru"
          value={formatNumber(data.feedback_total)}
          hint={`${problemAspects.length} aspek bermasalah`}
        />
      </div>

      {runs.unknown_category_runs > 0 && (
        <div className="alert alert-warning" style={{ marginBottom: 16 }}>
          <AlertTriangle size={18} />
          <div>
            <strong>{runs.unknown_category_runs} analisis memakai kategori yang tidak dikenali.</strong>{' '}
            Contoh: {runs.unknown_categories.map((c) => `"${c.category}" (${c.count}×)`).join(', ')}. Temuan
            ini tidak ikut dihitung dalam skor isi; perjelas instruksi AI agar memakai kategori baku.
          </div>
        </div>
      )}

      <div className="chart-grid" style={{ marginBottom: 16 }}>
        <section className="card">
          <div className="card-title">
            <div>
              <h2>Analisis AI terbaru</h2>
              <p>Dokumen yang terakhir diperiksa AI, berhasil atau gagal, dan penyebabnya.</p>
            </div>
            <Link to="/documents?ai=failed" className="btn btn-ghost btn-sm">
              Lihat yang gagal
            </Link>
          </div>
          {recentRuns.length === 0 ? (
            <EmptyState icon={Activity} title="Belum ada analisis AI pada periode ini" />
          ) : (
            <div className="run-list">
              {recentRuns.map((run) => (
                <Link
                  key={run.id}
                  to={`/documents/${run.document_id}`}
                  state={{ from: '/ai-performance' }}
                  className="run-row"
                >
                  <span className={`run-icon ${run.status === 'success' ? 'ok' : 'fail'}`}>
                    {run.status === 'success' ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
                  </span>
                  <span className="run-main">
                    <span className="cell-title" title={run.document_title}>
                      {run.document_title}
                    </span>
                    <span className="small muted">
                      {formatDateTime(run.created_at)}
                      {run.trigger === 'reanalyze' && ' · analisis ulang admin'}
                    </span>
                  </span>
                  <span className={`badge tone-${run.status === 'success' ? 'success' : 'error'}`}>
                    {run.status === 'success' ? 'Berhasil' : run.error_label || 'Gagal'}
                  </span>
                </Link>
              ))}
            </div>
          )}
        </section>

        <section className="card">
          <div className="card-title">
            <div>
              <h2>Penyebab AI gagal</h2>
              <p>Membantu memilih perbaikan: model, waktu tunggu, atau parser dokumen</p>
            </div>
          </div>
          <div className="chart-box small">
            {runs.failure_reasons.length === 0 ? (
              <EmptyState icon={CheckCircle2} title="Tidak ada kegagalan" />
            ) : (
              <Bar
                data={{
                  labels: runs.failure_reasons.map((r) => r.label),
                  datasets: [
                    {
                      label: 'Jumlah',
                      data: runs.failure_reasons.map((r) => r.count),
                      backgroundColor: COLORS.error,
                      borderRadius: 8,
                      maxBarThickness: 24,
                    },
                  ],
                }}
                options={{
                  indexAxis: 'y',
                  maintainAspectRatio: false,
                  plugins: { legend: { display: false } },
                  scales: {
                    x: { beginAtZero: true, ticks: { precision: 0 }, grid: { color: COLORS.grid } },
                    y: { grid: { display: false } },
                  },
                }}
              />
            )}
          </div>
        </section>
      </div>

      {retestAspect && (
        <RetestPanel
          key={`${retestAspect.source}-${retestAspect.aspect}`}
          aspect={retestAspect}
          onClose={() => setRetestAspect(null)}
          onDone={reload}
        />
      )}

      <section className="card" style={{ marginBottom: 16 }}>
        <div className="card-title">
          <div>
            <h2>Pola kesalahan per aspek</h2>
            <p>
              <strong>Temuan gagal</strong> = jumlah temuan &quot;gagal&quot; dari sistem.{' '}
              <strong>Ditandai keliru</strong> = yang dinilai admin sebagai kesalahan sistem. Aspek
              dengan persentase tinggi perlu diperbaiki.
            </p>
          </div>
        </div>
        <div className="table-wrap">
          <table className="table aspect-table">
            <thead>
              <tr>
                <th>Aspek</th>
                <th>Temuan gagal</th>
                <th>Ditandai keliru</th>
                <th style={{ minWidth: 160 }}>Persentase keliru</th>
                <th>Tindakan</th>
              </tr>
            </thead>
            <tbody>
              {aspects.map((a) => (
                <tr key={`${a.source}-${a.aspect}`} className={a.enabled ? '' : 'disabled-row'}>
                  <td>
                    <div style={{ fontWeight: 700 }}>{a.label}</div>
                    <span className="cell-sub">
                      {SOURCE_LABEL[a.source]}
                      {!a.enabled && ' · nonaktif'}
                    </span>
                  </td>
                  <td>{a.failed_count}</td>
                  <td>{a.feedback_count}</td>
                  <td>
                    {a.feedback_rate === null ? (
                      <span className="muted">-</span>
                    ) : (
                      <div className="rate-bar" title={`${a.feedback_rate}%`}>
                        <span
                          style={{
                            width: `${Math.min(a.feedback_rate, 100)}%`,
                            background: a.feedback_rate >= 30 ? COLORS.error : a.feedback_rate >= 10 ? COLORS.accent : COLORS.success,
                          }}
                        />
                        <em>{a.feedback_rate}%</em>
                      </div>
                    )}
                  </td>
                  <td>
                    <div className="row" style={{ flexWrap: 'nowrap' }}>
                      <Link
                        to={`/rules#${a.source}-${a.aspect}`}
                        className="btn btn-ghost btn-sm"
                        title="Ubah aturan atau instruksi AI untuk aspek ini"
                      >
                        <SlidersHorizontal size={14} /> Perbaiki
                      </Link>
                      <button
                        type="button"
                        className="btn btn-ghost btn-sm"
                        disabled={a.feedback_count === 0}
                        title={a.feedback_count === 0 ? 'Belum ada temuan keliru untuk diuji' : 'Uji ulang dokumen yang dulu keliru'}
                        onClick={() => {
                          setRetestAspect(a)
                          window.scrollTo({ top: 0, behavior: 'smooth' })
                        }}
                      >
                        <FlaskConical size={14} /> Uji ulang
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {problemAspects.length === 0 && (
          <p className="small muted" style={{ margin: '12px 0 0' }}>
            Belum ada temuan yang ditandai keliru. Tandai temuan yang salah di halaman detail dokumen agar
            pola kesalahan AI mulai terlihat.
          </p>
        )}
      </section>

      <div className="chart-grid">
        <section className="card">
          <div className="card-title">
            <div>
              <h2>Temuan keliru terbaru</h2>
              <p>Contoh nyata kesalahan sistem dari tinjauan admin</p>
            </div>
          </div>
          {recent.length === 0 ? (
            <EmptyState icon={Flag} title="Belum ada temuan keliru" />
          ) : (
            <div className="stack" style={{ gap: 10 }}>
              {recent.map((fb) => (
                <Link
                  key={fb.id}
                  to={`/documents/${fb.document_id}`}
                  state={{ from: '/ai-performance' }}
                  className="feedback-item"
                >
                  <div className="row" style={{ justifyContent: 'space-between' }}>
                    <strong>{fb.aspect_label}</strong>
                    <span className="small muted">versi {fb.rule_version}</span>
                  </div>
                  <div className="small">{fb.detail || '-'}</div>
                  <div className="small muted">
                    {fb.document_title} · {fb.created_by} · {formatDateTime(fb.created_at)}
                  </div>
                </Link>
              ))}
            </div>
          )}
        </section>

        <section className="card">
          <div className="card-title">
            <div>
              <h2>Riwayat versi aturan</h2>
              <p>Bandingkan kinerja AI sebelum &amp; sesudah aturan diubah</p>
            </div>
            <Link to="/rules" className="btn btn-ghost btn-sm">
              <SlidersHorizontal size={14} /> Ubah aturan
            </Link>
          </div>
          <div className="table-wrap">
            <table className="table" style={{ minWidth: 520 }}>
              <thead>
                <tr>
                  <th>Versi</th>
                  <th>Perubahan</th>
                  <th>Analisis</th>
                  <th>Berhasil</th>
                  <th>Ditandai keliru</th>
                </tr>
              </thead>
              <tbody>
                {versions.map((v) => (
                  <tr key={v.version} style={{ cursor: 'default' }}>
                    <td>
                      <strong>v{v.version}</strong>
                      {v.version === data.current_rule_version && (
                        <span className="badge tone-primary" style={{ marginLeft: 6 }}>
                          aktif
                        </span>
                      )}
                    </td>
                    <td>
                      <div className="small">{v.note || '-'}</div>
                      {v.created_at && (
                        <div className="cell-sub">
                          {v.created_by} · {formatDateTime(v.created_at)}
                        </div>
                      )}
                    </td>
                    <td>{v.runs}</td>
                    <td>{formatNumber(v.success_rate, '%')}</td>
                    <td>{v.feedback_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </>
  )
}
