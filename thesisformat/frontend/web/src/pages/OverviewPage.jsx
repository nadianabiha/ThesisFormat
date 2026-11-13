import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ArcElement,
  BarController,
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LineController,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
} from 'chart.js'
import { Bar, Chart, Doughnut } from 'react-chartjs-2'
import {
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  ClipboardCheck,
  FileText,
  Gauge,
  Users,
} from 'lucide-react'
import { getStats } from '../api/dashboard'
import { EmptyState, ErrorAlert, Spinner } from '../components/ui'
import { COLORS } from '../utils/constants'
import { formatNumber, formatShortDate } from '../utils/format'
import { useAsync } from '../utils/useAsync'

ChartJS.register(
  ArcElement,
  BarController,
  BarElement,
  CategoryScale,
  Filler,
  Legend,
  LineController,
  LineElement,
  LinearScale,
  PointElement,
  Tooltip,
)

ChartJS.defaults.font.family = getComputedStyle(document.documentElement).fontFamily
ChartJS.defaults.color = COLORS.text

const gridScale = {
  grid: { color: COLORS.grid },
  border: { display: false },
}

function StatCard({ icon: Icon, color, label, value, hint, to }) {
  const body = (
    <>
      <div className="stat-top">
        <span className="stat-label">{label}</span>
        <span className="stat-icon" style={{ background: `${color}1f`, color }}>
          <Icon size={20} />
        </span>
      </div>
      <div className="stat-value">{value}</div>
      {hint && <div className="stat-hint">{hint}</div>}
    </>
  )
  return to ? (
    <Link to={to} className="card stat-card">
      {body}
    </Link>
  ) : (
    <div className="card stat-card">{body}</div>
  )
}

function ChartCard({ title, subtitle, small, children }) {
  return (
    <section className="card">
      <div className="card-title">
        <div>
          <h2>{title}</h2>
          {subtitle && <p>{subtitle}</p>}
        </div>
      </div>
      <div className={`chart-box${small ? ' small' : ''}`}>{children}</div>
    </section>
  )
}

export default function OverviewPage() {
  const [weeks, setWeeks] = useState(8)
  const { data, loading, error, reload } = useAsync(() => getStats(weeks), [weeks])

  if (!data && loading) return <Spinner />
  if (!data && error) return <ErrorAlert error={error} onRetry={reload} />

  const { overview, score_by_type, score_distribution, trend, top_findings } = data
  const pending = overview.review.pending

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Ringkasan</h1>
          <p>Statistik hasil pemeriksaan format karya tulis mahasiswa.</p>
        </div>
        <div className="field" style={{ minWidth: 180 }}>
          <label htmlFor="weeks">Periode tren</label>
          <select
            id="weeks"
            className="select"
            value={weeks}
            onChange={(e) => setWeeks(Number(e.target.value))}
          >
            <option value={4}>4 minggu terakhir</option>
            <option value={8}>8 minggu terakhir</option>
            <option value={12}>12 minggu terakhir</option>
            <option value={26}>26 minggu terakhir</option>
          </select>
        </div>
      </div>

      {error && (
        <div style={{ marginBottom: 16 }}>
          <ErrorAlert error={error} onRetry={reload} />
        </div>
      )}

      <div className="stat-grid">
        <StatCard
          icon={FileText}
          color={COLORS.primary}
          label="Total dokumen"
          value={formatNumber(overview.total_documents)}
          hint={`+${overview.documents_this_week} dalam 7 hari terakhir`}
          to="/documents"
        />
        <StatCard
          icon={Users}
          color={COLORS.info}
          label="Mahasiswa"
          value={formatNumber(overview.total_students)}
          hint="Akun terdaftar"
        />
        <StatCard
          icon={Gauge}
          color={COLORS.accent}
          label="Rata-rata skor"
          value={formatNumber(overview.average_score)}
          hint="Skala 0–100"
        />
        <StatCard
          icon={CheckCircle2}
          color={COLORS.success}
          label="Memenuhi standar"
          value={formatNumber(overview.passing_rate, '%')}
          hint={`${overview.passing_count} dokumen skor ≥ ${overview.passing_score}`}
        />
        <StatCard
          icon={AlertTriangle}
          color={COLORS.error}
          label="Perlu perbaikan"
          value={formatNumber(overview.needs_improvement)}
          hint={`Skor di bawah ${overview.passing_score}`}
        />
        <StatCard
          icon={BrainCircuit}
          color={COLORS.primary}
          label="Analisis AI berhasil"
          value={formatNumber(overview.ai_success_rate, '%')}
          hint="Dokumen dengan skor semantik"
        />
        <StatCard
          icon={ClipboardCheck}
          color={COLORS.accent}
          label="Menunggu review"
          value={formatNumber(pending)}
          hint={`${overview.review.validated} tervalidasi · ${overview.review.corrected} dikoreksi`}
          to="/documents?review_status=pending"
        />
      </div>

      <div className="chart-grid">
        <ChartCard
          title="Tren unggahan"
          subtitle="Jumlah dokumen dan rata-rata skor per minggu"
        >
          <Chart
            type="bar"
            data={{
              labels: trend.map((t) => formatShortDate(t.week_start)),
              datasets: [
                {
                  type: 'bar',
                  label: 'Dokumen diunggah',
                  data: trend.map((t) => t.uploads),
                  backgroundColor: COLORS.primarySoft,
                  borderRadius: 8,
                  yAxisID: 'y',
                  order: 2,
                },
                {
                  type: 'line',
                  label: 'Rata-rata skor',
                  data: trend.map((t) => t.average_score),
                  borderColor: COLORS.accent,
                  backgroundColor: COLORS.accent,
                  tension: 0.35,
                  spanGaps: true,
                  yAxisID: 'y1',
                  order: 1,
                },
              ],
            }}
            options={{
              maintainAspectRatio: false,
              interaction: { mode: 'index', intersect: false },
              plugins: { legend: { position: 'bottom' } },
              scales: {
                x: { ...gridScale, grid: { display: false } },
                y: { ...gridScale, beginAtZero: true, ticks: { precision: 0 }, title: { display: true, text: 'Dokumen' } },
                y1: {
                  ...gridScale,
                  position: 'right',
                  min: 0,
                  max: 100,
                  grid: { drawOnChartArea: false },
                  title: { display: true, text: 'Skor' },
                },
              },
            }}
          />
        </ChartCard>

        <ChartCard title="Rata-rata skor per jenis dokumen" subtitle="Jenis Panduan Penulisan Polinela">
          <Bar
            data={{
              labels: score_by_type.map((t) => t.label),
              datasets: [
                {
                  label: 'Rata-rata skor',
                  data: score_by_type.map((t) => t.average_score),
                  backgroundColor: COLORS.primary,
                  borderRadius: 8,
                  maxBarThickness: 28,
                },
              ],
            }}
            options={{
              indexAxis: 'y',
              maintainAspectRatio: false,
              plugins: {
                legend: { display: false },
                tooltip: {
                  callbacks: {
                    afterLabel: (ctx) => `${score_by_type[ctx.dataIndex].count} dokumen`,
                  },
                },
              },
              scales: {
                x: { ...gridScale, min: 0, max: 100 },
                y: { ...gridScale, grid: { display: false } },
              },
            }}
          />
        </ChartCard>

        <ChartCard title="Sebaran skor" subtitle="Jumlah dokumen per rentang skor" small>
          {score_distribution.every((b) => b.count === 0) ? (
            <EmptyState title="Belum ada skor" />
          ) : (
            <Doughnut
              data={{
                labels: score_distribution.map((b) => b.label),
                datasets: [
                  {
                    data: score_distribution.map((b) => b.count),
                    backgroundColor: [COLORS.error, COLORS.accent, COLORS.primary, COLORS.success],
                    borderWidth: 0,
                  },
                ],
              }}
              options={{
                maintainAspectRatio: false,
                cutout: '62%',
                plugins: { legend: { position: 'right' } },
              }}
            />
          )}
        </ChartCard>

        <ChartCard title="Pelanggaran paling sering" subtitle="Temuan berstatus gagal (format & isi)" small>
          {top_findings.length === 0 ? (
            <EmptyState title="Belum ada pelanggaran" />
          ) : (
            <Bar
              data={{
                labels: top_findings.map((f) => f.title),
                datasets: [
                  {
                    label: 'Jumlah temuan',
                    data: top_findings.map((f) => f.count),
                    backgroundColor: top_findings.map((f) =>
                      f.source === 'semantic' ? COLORS.accent : COLORS.primary,
                    ),
                    borderRadius: 8,
                    maxBarThickness: 22,
                  },
                ],
              }}
              options={{
                indexAxis: 'y',
                maintainAspectRatio: false,
                plugins: {
                  legend: { display: false },
                  tooltip: {
                    callbacks: {
                      afterLabel: (ctx) =>
                        top_findings[ctx.dataIndex].source === 'semantic'
                          ? 'Aspek isi (AI)'
                          : 'Aspek format',
                    },
                  },
                },
                scales: {
                  x: { ...gridScale, beginAtZero: true, ticks: { precision: 0 } },
                  y: { ...gridScale, grid: { display: false } },
                },
              }}
            />
          )}
        </ChartCard>
      </div>
    </>
  )
}
