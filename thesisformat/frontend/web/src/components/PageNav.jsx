import { useLocation, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'

/**
 * Satu tombol "Kembali" ke halaman induk.
 * - Ke alamat yang dikirim halaman asal (state.from), mis. daftar
 *   dokumen lengkap dengan filternya.
 * - Jika tidak ada (mis. halaman dibuka langsung dari URL), ke `fallback`.
 * `label` = nama halaman tujuan, mis. "Ringkasan".
 */
export default function PageNav({ label, fallback = '/' }) {
  const navigate = useNavigate()
  const location = useLocation()

  return (
    <div className="page-nav">
      <button
        type="button"
        className="back-btn"
        onClick={() => navigate(location.state?.from ?? fallback)}
      >
        <ArrowLeft size={16} />
        Kembali ke {label}
      </button>
    </div>
  )
}
