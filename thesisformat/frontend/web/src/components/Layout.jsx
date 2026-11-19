import { useEffect, useRef, useState } from 'react'
import { Link, NavLink, Outlet, useLocation } from 'react-router-dom'
import {
  BookOpenCheck,
  BrainCircuit,
  ChevronDown,
  FileText,
  LayoutDashboard,
  LogOut,
  Menu,
  SlidersHorizontal,
  Users,
  X,
} from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import { BlobIllustration } from './ui'

const NAV_ITEMS = [
  { to: '/', label: 'Ringkasan', icon: LayoutDashboard, end: true },
  { to: '/documents', label: 'Dokumen', icon: FileText },
  { to: '/students', label: 'Mahasiswa', icon: Users },
  { to: '/ai-performance', label: 'Kinerja AI', icon: BrainCircuit },
  { to: '/rules', label: 'Aturan AI', icon: SlidersHorizontal },
]

/** Menu profil di pojok kanan atas: nama admin + tombol Keluar. */
function UserMenu({ user, onLogout }) {
  const [open, setOpen] = useState(false)
  const ref = useRef(null)
  const initial = (user?.name || '?').trim().charAt(0).toUpperCase()

  // Tutup saat klik di luar menu atau menekan Esc.
  useEffect(() => {
    if (!open) return undefined
    const onClick = (event) => {
      if (ref.current && !ref.current.contains(event.target)) setOpen(false)
    }
    const onKey = (event) => event.key === 'Escape' && setOpen(false)
    document.addEventListener('mousedown', onClick)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onClick)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  return (
    <div className="user-menu" ref={ref}>
      <button
        type="button"
        className="user-menu-button"
        aria-haspopup="menu"
        aria-expanded={open}
        onClick={() => setOpen((value) => !value)}
      >
        <span className="avatar">{initial}</span>
        <span className="user-menu-text">
          <span className="name">{user?.name}</span>
          <span className="role">Admin</span>
        </span>
        <ChevronDown size={16} className={`chevron${open ? ' open' : ''}`} />
      </button>

      {open && (
        <div className="user-menu-panel" role="menu">
          <div className="user-menu-info">
            <strong>{user?.name}</strong>
            {user?.email && <span>{user.email}</span>}
          </div>
          <button type="button" role="menuitem" className="user-menu-item danger" onClick={onLogout}>
            <LogOut size={16} />
            Keluar
          </button>
        </div>
      )}
    </div>
  )
}

export default function Layout() {
  const { user, logout } = useAuth()
  const [drawerOpen, setDrawerOpen] = useState(false)
  const location = useLocation()

  // Tutup menu laci (HP/tablet) setiap pindah halaman.
  useEffect(() => setDrawerOpen(false), [location.pathname])

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
          <BlobIllustration size={88} icon={BrainCircuit} />
          <strong>Apakah AI sudah bekerja optimal?</strong>
          <p>Amati pola kesalahan AI, lalu perbaiki aturannya.</p>
          <Link to="/ai-performance" className="btn btn-accent btn-sm">
            Pantau AI
          </Link>
        </div>
      </aside>

      <div className="drawer-backdrop" onClick={() => setDrawerOpen(false)} />

      <div className="main">
        <header className="topbar">
          {/* Tombol menu & judul hanya tampil di HP/tablet (lihat CSS). */}
          <button
            type="button"
            className="icon-btn topbar-menu"
            aria-label={drawerOpen ? 'Tutup menu' : 'Buka menu'}
            onClick={() => setDrawerOpen((open) => !open)}
          >
            {drawerOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <span className="topbar-title">ThesisFormat Admin</span>

          {/* Tempat tombol "Kembali" dari setiap halaman (lihat PageNav),
              agar sejajar dengan menu profil. */}
          <div id="topbar-slot" className="topbar-slot" />

          <UserMenu user={user} onLogout={logout} />
        </header>

        <main className="content">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
