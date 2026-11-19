import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'
import { useLocation, useNavigate } from 'react-router-dom'
import { ArrowLeft } from 'lucide-react'

/**
 * Satu tombol "Kembali" ke halaman induk, ditampilkan di bilah atas
 * (sejajar dengan menu profil admin, lihat Layout #topbar-slot).
 * - Ke alamat yang dikirim halaman asal (state.from), mis. daftar
 *   dokumen lengkap dengan filternya.
 * - Jika tidak ada (mis. halaman dibuka langsung dari URL), ke `fallback`.
 * `label` = nama halaman tujuan, mis. "Ringkasan".
 */
export default function PageNav({ label, fallback = '/' }) {
  const navigate = useNavigate()
  const location = useLocation()
  const [slot, setSlot] = useState(null)

  // Cari tempat di bilah atas setelah halaman tampil.
  useEffect(() => setSlot(document.getElementById('topbar-slot')), [])

  const button = (
    <button
      type="button"
      className="back-btn"
      onClick={() => navigate(location.state?.from ?? fallback)}
    >
      <ArrowLeft size={16} />
      Kembali<span className="back-btn-target">ke {label}</span>
    </button>
  )

  // Jika bilah atas tidak ada (mis. dipakai di luar Layout), tampil biasa.
  return slot ? createPortal(button, slot) : <div className="page-nav">{button}</div>
}
