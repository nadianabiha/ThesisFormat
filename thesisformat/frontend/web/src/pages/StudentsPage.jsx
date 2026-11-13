import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Search, Users } from 'lucide-react'
import { getStudents } from '../api/dashboard'
import PageNav from '../components/PageNav'
import { EmptyState, ErrorAlert, ScoreRing, Spinner } from '../components/ui'
import { formatDate, formatDateTime } from '../utils/format'
import { useAsync } from '../utils/useAsync'

export default function StudentsPage() {
  const navigate = useNavigate()
  const [searchInput, setSearchInput] = useState('')
  const [search, setSearch] = useState('')

  // Tunggu pengguna berhenti mengetik (300 ms) sebelum mencari.
  useEffect(() => {
    const timer = setTimeout(() => setSearch(searchInput.trim()), 300)
    return () => clearTimeout(timer)
  }, [searchInput])

  const { data, loading, error, reload } = useAsync(() => getStudents(search), [search])
  const students = data?.results ?? []

  // Buka dokumen milik mahasiswa; tombol Kembali di sana kembali ke sini.
  const documentsUrl = (student) => `/documents?search=${encodeURIComponent(student.email)}`
  const open = (student) => navigate(documentsUrl(student), { state: { from: '/students' } })

  return (
    <>
      <PageNav label="Ringkasan" fallback="/" />

      <div className="page-header">
        <div>
          <h1>Mahasiswa</h1>
          <p>Akun mahasiswa yang terdaftar beserta ringkasan dokumennya.</p>
        </div>
      </div>

      <section className="card">
        <div className="filters" style={{ gridTemplateColumns: 'minmax(0, 1fr)' }}>
          <div className="field">
            <label htmlFor="student-search">Cari</label>
            <div className="input-icon">
              <Search size={18} />
              <input
                id="student-search"
                className="input"
                placeholder="Nama atau email mahasiswa"
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
              />
            </div>
          </div>
        </div>

        {error && <ErrorAlert error={error} onRetry={reload} />}

        {loading && !data ? (
          <Spinner />
        ) : students.length === 0 && !error ? (
          <EmptyState icon={Users} title="Tidak ada mahasiswa">
            Coba ubah kata kunci pencarian.
          </EmptyState>
        ) : (
          <div style={{ opacity: loading ? 0.6 : 1, transition: 'opacity .15s' }}>
            {/* Tablet & desktop: tabel */}
            <div className="table-wrap">
              <table className="table">
                <thead>
                  <tr>
                    <th>Mahasiswa</th>
                    <th>Dokumen</th>
                    <th>Rata-rata skor</th>
                    <th>Menunggu review</th>
                    <th>Unggahan terakhir</th>
                    <th>Terdaftar</th>
                  </tr>
                </thead>
                <tbody>
                  {students.map((student) => (
                    <tr
                      key={student.id}
                      tabIndex={0}
                      onClick={() => open(student)}
                      onKeyDown={(e) => e.key === 'Enter' && open(student)}
                      title="Lihat dokumen mahasiswa ini"
                    >
                      <td>
                        <div className="row" style={{ flexWrap: 'nowrap', gap: 12 }}>
                          <span className="avatar">
                            {(student.name || '?').charAt(0).toUpperCase()}
                          </span>
                          <div style={{ minWidth: 0 }}>
                            <div className="cell-title">{student.name}</div>
                            <div className="cell-sub">{student.email}</div>
                          </div>
                        </div>
                      </td>
                      <td>{student.document_count}</td>
                      <td>
                        <ScoreRing score={student.average_score === null ? null : Math.round(student.average_score)} size={44} stroke={5} />
                      </td>
                      <td>
                        {student.pending_review > 0 ? (
                          <span className="badge tone-warning">{student.pending_review} dokumen</span>
                        ) : (
                          <span className="muted">-</span>
                        )}
                      </td>
                      <td className="muted small">{formatDateTime(student.last_upload)}</td>
                      <td className="muted small">{formatDate(student.date_joined)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* HP: kartu */}
            <div className="doc-cards">
              {students.map((student) => (
                <Link
                  key={student.id}
                  to={documentsUrl(student)}
                  state={{ from: '/students' }}
                  className="doc-card"
                >
                  <div className="doc-card-row" style={{ flexWrap: 'nowrap' }}>
                    <span className="avatar">{(student.name || '?').charAt(0).toUpperCase()}</span>
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <div className="cell-title" style={{ maxWidth: '100%' }}>
                        {student.name}
                      </div>
                      <div className="cell-sub">{student.email}</div>
                    </div>
                    <ScoreRing score={student.average_score === null ? null : Math.round(student.average_score)} size={46} stroke={5} />
                  </div>
                  <div className="doc-card-row small muted">
                    <span>{student.document_count} dokumen</span>
                    {student.pending_review > 0 && (
                      <span className="badge tone-warning">{student.pending_review} menunggu review</span>
                    )}
                  </div>
                </Link>
              ))}
            </div>

            <div className="pagination">
              <span>{data?.count ?? 0} mahasiswa</span>
            </div>
          </div>
        )}
      </section>
    </>
  )
}
