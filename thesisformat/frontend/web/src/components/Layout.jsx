import { useEffect, useState } from 'react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import {
  BookOpenCheck,
  ClipboardCheck,
  FileText,
  LayoutDashboard,
  LogOut,
  Menu,
  Users,
  X,
} from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import { BlobIllustration } from './ui'

const NAV_ITEMS = [
  { to: '/', label: 'Ringkasan', icon: LayoutDashboard, end: true },
  { to: '/documents', label: 'Dokumen', icon: FileText },
  { to: '/students', label: 'Mahasiswa', icon: Users },
]

export default function Layout() {
  const { user, logout } = useAuth()
  const [drawerOpen, setDrawerOpen] = useState(false)
  const location = useLocation()

  // Tutup menu laci (HP/tablet) setiap pindah halaman.
  useEffect(() => setDrawerOpen(false), [location.pathname])

  const initial = (user?.name || '?').trim().charAt(0).toUpperCase()

  return (
    <div className={`app-shell${drawerOpen ? ' drawer-open' : ''}`}>
      <aside className="sidebar" aria-label="Navigasi utama">
        <div className="brand">
          <div className="brand-icon">
            <BookOpenCheck size={22} />
          </div>
          <div>
            ThesisFormat
            <small>Dashboard Admin</small>
          </div>
        </div>

        <nav className="nav">
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink key={to} to={to} end={end}>
              <Icon size={20} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="side-promo">
          <BlobIllustration size={88} icon={ClipboardCheck} />
          <strong>Hasil AI perlu dicek?</strong>
          <p>Validasi atau koreksi sebelum dipakai mahasiswa.</p>
          <Link to="/documents?review_status=pending" className="btn btn-accent btn-sm">
            Lihat antrean
          </Link>
        </div>

        <div className="sidebar-footer">
          <div className="user-chip">
            <div className="avatar">{initial}</div>
            <div style={{ minWidth: 0 }}>
              <div className="name">{user?.name}</div>
              <div className="role">Admin</div>
            </div>
          </div>
          <button type="button" className="btn btn-ghost btn-block" onClick={logout}>
            <LogOut size={16} />
            Keluar
          </button>
        </div>
      </aside>

      <div className="drawer-backdrop" onClick={() => setDrawerOpen(false)} />

      <div className="main">
        <header className="topbar">
          <button
            type="button"
            className="icon-btn"
            aria-label={drawerOpen ? 'Tutup menu' : 'Buka menu'}
            onClick={() => setDrawerOpen((open) => !open)}
          >
            {drawerOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          ThesisFormat Admin
        </header>

        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
