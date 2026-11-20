import { useEffect, useState } from 'react'
import { Link, useLocation, useNavigate, useSearchParams } from 'react-router-dom'
import {
  ChevronLeft,
  ChevronRight,
  FileSearch,
  Filter,
  LayoutGrid,
  Search,
  X,
} from 'lucide-react'
import { getDocuments } from '../api/dashboard'
import PageNav from '../components/PageNav'
import {
  DocTypeIcon,
  EmptyState,
  ErrorAlert,
  PillChip,
  ReviewBadge,
  ScoreRing,
  Spinner,
  TypeBadge,
  typeIcon,
} from '../components/ui'
import {
  DOCUMENT_TYPES,
  REVIEW_STATUS,
  documentType as documentTypeInfo,
} from '../utils/constants'
import { formatDateTime } from '../utils/format'
import { useAsync } from '../utils/useAsync'

const PAGE_SIZE = 10

const ORDERING = [
  { value: 'newest', label: 'Terbaru' },
  { value: 'oldest', label: 'Terlama' },
  { value: 'score_low', label: 'Skor terendah' },
  { value: 'score_high', label: 'Skor tertinggi' },
]

// Pilihan rentang skor (dipakai juga oleh kartu di halaman Ringkasan).
const SCORE_FILTERS = [
  { value: '', label: 'Semua skor' },
  { value: 'pass', label: 'Memenuhi standar (≥ 75)', min: '75', max: '' },
  { value: 'fail', label: 'Perlu perbaikan (< 75)', min: '', max: '74' },
  { value: 'excellent', label: 'Sangat baik (≥ 90)', min: '90', max: '' },
]

const AI_FILTERS = {
  success: 'Analisis AI berhasil',
  failed: 'Analisis AI gagal',
}

export default function DocumentsPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [params, setParams] = useSearchParams()

  const search = params.get('search') ?? ''
  const documentType = params.get('document_type') ?? ''
  const reviewStatus = params.get('review_status') ?? ''
  const ordering = params.get('ordering') ?? 'newest'
  const scoreMin = params.get('score_min') ?? ''
  const scoreMax = params.get('score_max') ?? ''
  const ai = params.get('ai') ?? ''
  const page = Number(params.get('page') ?? 1)

  const scoreFilter =
    SCORE_FILTERS.find((f) => f.value && f.min === scoreMin && f.max === scoreMax) ??
    (scoreMin || scoreMax
      ? { value: 'custom', label: `Skor ${scoreMin || 0}–${scoreMax || 100}` }
      : SCORE_FILTERS[0])

  // Halaman asal (mis. /students) agar label tombol Kembali sesuai.
  const cameFrom = location.state?.from

  // Kolom pencarian: tunggu pengguna berhenti mengetik (300 ms).
  const [searchInput, setSearchInput] = useState(search)
  useEffect(() => setSearchInput(search), [search])
  useEffect(() => {
    if (searchInput === search) return undefined
    const timer = setTimeout(() => updateParams({ search: searchInput }), 300)
    return () => clearTimeout(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchInput])

  function updateParams(changes, resetPage = true) {
    const next = new URLSearchParams(params)
    Object.entries(changes).forEach(([key, value]) => {
      if (value === '' || value === null || value === undefined) next.delete(key)
      else next.set(key, value)
    })
    if (resetPage && !('page' in changes)) next.delete('page')
    // state ikut dibawa agar tombol Kembali tetap ke halaman asal.
    setParams(next, { replace: true, state: location.state })
  }

  const { data, loading, error, reload } = useAsync(
    () =>
      getDocuments({
        search,
        document_type: documentType,
        review_status: reviewStatus,
        ordering,
        score_min: scoreMin,
        score_max: scoreMax,
        ai,
        page,
        page_size: PAGE_SIZE,
      }),
    [search, documentType, reviewStatus, ordering, scoreMin, scoreMax, ai, page],
  )

  const results = data?.results ?? []

  // Alamat daftar saat ini (lengkap dengan filter), dikirim ke halaman
  // detail agar tombol "Kembali" membuka daftar yang sama.
  const listUrl = `/documents${location.search}`
  const open = (id) => navigate(`/documents/${id}`, { state: { from: listUrl } })

  // Ringkasan filter yang sedang aktif.
  const activeFilters = [
    search && `kata kunci "${search}"`,
    documentType && documentTypeInfo(documentType).short,
    reviewStatus &&
      (reviewStatus === 'none' ? 'Belum ada hasil' : REVIEW_STATUS[reviewStatus]?.label),
    scoreFilter.value && scoreFilter.label,
    AI_FILTERS[ai],
  ].filter(Boolean)

  return (
    <>
      <PageNav label={cameFrom === '/students' ? 'Mahasiswa' : 'Ringkasan'} fallback="/" />

      <div className="page-header">
        <div>
          <h1>Dokumen</h1>
          <p>Semua dokumen yang diunggah mahasiswa melalui aplikasi mobile.</p>
        </div>
      </div>

      <section className="card">
        {activeFilters.length > 0 && (
          <div className="filter-info" role="status">
            <Filter size={16} />
            <span>
              Menampilkan: <strong>{activeFilters.join(' · ')}</strong>
            </span>
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={() => {
                setSearchInput('')
                setParams(ordering === 'newest' ? {} : { ordering }, {
                  replace: true,
                  state: location.state,
                })
              }}
            >
              <X size={14} /> Hapus filter
            </button>
          </div>
        )}
        <div className="filters">
          <div className="field filter-search">
            <label htmlFor="search">Cari</label>
            <div className="input-icon">
              <Search size={18} />
              <input
                id="search"
                className="input"
                placeholder="Nama file, nama, atau email mahasiswa"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
              />
            </div>
          </div>

          <div className="field">
            <label htmlFor="review_status">Status review</label>
            <select
              id="review_status"
              className="select"
              value={reviewStatus}
              onChange={(e) => updateParams({ review_status: e.target.value })}
            >
              <option value="">Semua status</option>
              {Object.entries(REVIEW_STATUS).map(([value, info]) => (
                <option key={value} value={value}>
                  {info.label}
                </option>
              ))}
              <option value="none">Belum ada hasil</option>
            </select>
          </div>

          <div className="field">
            <label htmlFor="score">Skor</label>
            <select
              id="score"
              className="select"
              value={scoreFilter.value}
              onChange={(e) => {
                const choice = SCORE_FILTERS.find((f) => f.value === e.target.value)
                updateParams({ score_min: choice?.min ?? '', score_max: choice?.max ?? '' })
              }}
            >
              {SCORE_FILTERS.map((f) => (
                <option key={f.value} value={f.value}>
                  {f.label}
                </option>
              ))}
              {scoreFilter.value === 'custom' && (
                <option value="custom">{scoreFilter.label}</option>
              )}
            </select>
          </div>

          <div className="field">
            <label htmlFor="ai">Analisis AI</label>
            <select
              id="ai"
              className="select"
              value={ai}
              onChange={(e) => updateParams({ ai: e.target.value })}
            >
              <option value="">Semua</option>
              <option value="success">Berhasil</option>
              <option value="failed">Gagal</option>
            </select>
          </div>

          <div className="field">
            <label htmlFor="ordering">Urutkan</label>
            <select
              id="ordering"
              className="select"
              value={ordering}
              onChange={(e) => updateParams({ ordering: e.target.value })}
            >
              {ORDERING.map((o) => (
                <option key={o.value} value={o.value}>
                  {o.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Filter jenis dokumen: chip pil berwarna seperti di app mobile */}
        <div className="chip-row" role="group" aria-label="Filter jenis dokumen">
          <PillChip
            label="Semua"
            icon={LayoutGrid}
            selected={!documentType}
            onClick={() => updateParams({ document_type: '' })}
          />
          {DOCUMENT_TYPES.map((type) => (
            <PillChip
              key={type.id}
              label={type.short}
              icon={typeIcon(type.id)}
              color={type.color}
              selected={documentType === type.id}
              onClick={() => updateParams({ document_type: type.id })}
            />
          ))}
        </div>

        {error && <ErrorAlert error={error} onRetry={reload} />}

        {loading && !data ? (
          <Spinner />
        ) : results.length === 0 && !error ? (
          <EmptyState icon={FileSearch} title="Tidak ada dokumen">
            Coba ubah kata kunci atau filter.
          </EmptyState>
        ) : (
          <div style={{ opacity: loading ? 0.6 : 1, transition: 'opacity .15s' }}>
            {/* Tablet & desktop: tabel */}
            <div className="table-wrap has-cards">
              <table className="table">
                <thead>
                  <tr>
                    <th>Dokumen</th>
                    <th>Mahasiswa</th>
                    <th>Diunggah</th>
                    <th>Skor</th>
                    <th>Temuan gagal</th>
                    <th>Status review</th>
                  </tr>
                </thead>
                <tbody>
                  {results.map((doc) => (
                    <tr
                      key={doc.id}
                      tabIndex={0}
                      onClick={() => open(doc.id)}
                      onKeyDown={(e) => e.key === 'Enter' && open(doc.id)}
                    >
                      <td>
                        <div className="row" style={{ flexWrap: 'nowrap', gap: 12 }}>
                          <DocTypeIcon type={doc.document_type} size={40} />
                          <div style={{ minWidth: 0 }}>
                            <div className="cell-title" title={doc.title}>
                              {doc.title}
                            </div>
                            <TypeBadge type={doc.document_type} />
                          </div>
                        </div>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{doc.student.name}</div>
                        <div className="cell-sub">{doc.student.email}</div>
                      </td>
                      <td className="muted small" style={{ whiteSpace: 'nowrap' }}>
                        {formatDateTime(doc.uploaded_at)}
                      </td>
                      <td>
                        <ScoreRing score={doc.has_semantic_score ? doc.score : null} size={44} stroke={5} />
                      </td>
                      <td>{doc.has_result ? doc.failed_findings : '-'}</td>
                      <td>
                        <ReviewBadge status={doc.review_status} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* HP: kartu */}
            <div className="doc-cards">
              {results.map((doc) => (
                <Link
                  key={doc.id}
                  to={`/documents/${doc.id}`}
                  state={{ from: listUrl }}
                  className="doc-card"
                >
                  <div className="doc-card-row" style={{ flexWrap: 'nowrap' }}>
                    <DocTypeIcon type={doc.document_type} size={40} />
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <div className="cell-title" style={{ maxWidth: '100%' }}>
                        {doc.title}
                      </div>
                      <TypeBadge type={doc.document_type} />
                    </div>
                    <ScoreRing score={doc.has_semantic_score ? doc.score : null} size={46} stroke={5} />
                  </div>
                  <div className="small muted">
                    {doc.student.name} · {formatDateTime(doc.uploaded_at)}
                  </div>
                  <div className="doc-card-row">
                    <ReviewBadge status={doc.review_status} />
                    {doc.has_result && (
                      <span className="small muted">{doc.failed_findings} temuan gagal</span>
                    )}
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}

        {data && data.count > 0 && (
          <div className="pagination">
            <span>
              Halaman {data.page} dari {data.total_pages} · {data.count} dokumen
            </span>
            <div className="buttons">
              <button
                type="button"
                className="btn btn-ghost btn-sm"
                disabled={data.page <= 1}
                onClick={() => updateParams({ page: data.page - 1 }, false)}
              >
                <ChevronLeft size={16} /> Sebelumnya
              </button>
              <button
                type="button"
                className="btn btn-ghost btn-sm"
                disabled={data.page >= data.total_pages}
                onClick={() => updateParams({ page: data.page + 1 }, false)}
              >
                Berikutnya <ChevronRight size={16} />
              </button>
            </div>
          </div>
        )}
      </section>
    </>
  )
}
