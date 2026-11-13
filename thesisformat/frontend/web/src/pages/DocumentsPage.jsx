import { useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { ChevronLeft, ChevronRight, FileSearch, Search } from 'lucide-react'
import { getDocuments } from '../api/dashboard'
import { EmptyState, ErrorAlert, ReviewBadge, ScoreRing, Spinner, TypeBadge } from '../components/ui'
import { DOCUMENT_TYPES, REVIEW_STATUS } from '../utils/constants'
import { formatDateTime } from '../utils/format'
import { useAsync } from '../utils/useAsync'

const PAGE_SIZE = 10

const ORDERING = [
  { value: 'newest', label: 'Terbaru' },
  { value: 'oldest', label: 'Terlama' },
  { value: 'score_low', label: 'Skor terendah' },
  { value: 'score_high', label: 'Skor tertinggi' },
]

export default function DocumentsPage() {
  const navigate = useNavigate()
  const [params, setParams] = useSearchParams()

  const search = params.get('search') ?? ''
  const documentType = params.get('document_type') ?? ''
  const reviewStatus = params.get('review_status') ?? ''
  const ordering = params.get('ordering') ?? 'newest'
  const page = Number(params.get('page') ?? 1)

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
    setParams(next, { replace: true })
  }

  const { data, loading, error, reload } = useAsync(
    () =>
      getDocuments({
        search,
        document_type: documentType,
        review_status: reviewStatus,
        ordering,
        page,
        page_size: PAGE_SIZE,
      }),
    [search, documentType, reviewStatus, ordering, page],
  )

  const results = data?.results ?? []
  const open = (id) => navigate(`/documents/${id}`)

  return (
    <>
      <div className="page-header">
        <div>
          <h1>Dokumen</h1>
          <p>Semua dokumen yang diunggah mahasiswa melalui aplikasi mobile.</p>
        </div>
      </div>

      <section className="card">
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
            <label htmlFor="document_type">Jenis dokumen</label>
            <select
              id="document_type"
              className="select"
              value={documentType}
              onChange={(e) => updateParams({ document_type: e.target.value })}
            >
              <option value="">Semua jenis</option>
              {DOCUMENT_TYPES.map((type) => (
                <option key={type.id} value={type.id}>
                  {type.label}
                </option>
              ))}
            </select>
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
            <div className="table-wrap">
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
                        <div className="cell-title" title={doc.title}>
                          {doc.title}
                        </div>
                        <TypeBadge type={doc.document_type} />
                      </td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{doc.student.name}</div>
                        <div className="cell-sub">{doc.student.email}</div>
                      </td>
                      <td className="muted small" style={{ whiteSpace: 'nowrap' }}>
                        {formatDateTime(doc.uploaded_at)}
                      </td>
                      <td>
                        <ScoreRing score={doc.score} size={44} stroke={5} />
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
                <Link key={doc.id} to={`/documents/${doc.id}`} className="doc-card">
                  <div className="doc-card-row" style={{ flexWrap: 'nowrap' }}>
                    <div style={{ minWidth: 0 }}>
                      <div className="cell-title" style={{ maxWidth: '100%' }}>
                        {doc.title}
                      </div>
                      <TypeBadge type={doc.document_type} />
                    </div>
                    <ScoreRing score={doc.score} size={46} stroke={5} />
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
