import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import {
  BarChart3,
  BookOpenCheck,
  Eye,
  EyeOff,
  Lock,
  Mail,
  ShieldCheck,
  Sparkles,
} from 'lucide-react'
import { useAuth } from '../auth/AuthContext'
import { BlobIllustration, ErrorAlert } from '../components/ui'

const FEATURES = [
  { icon: BarChart3, text: 'Statistik hasil pemeriksaan format karya tulis' },
  { icon: Sparkles, text: 'Tinjau dan koreksi hasil penilaian AI' },
  { icon: ShieldCheck, text: 'Validasi sebelum hasil dipakai mahasiswa' },
]

export default function LoginPage() {
  const { user, login } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  if (user) return <Navigate to="/" replace />

  async function handleSubmit(event) {
    event.preventDefault()
    if (!identifier.trim() || !password) {
      setError(new Error('Email/username dan password wajib diisi.'))
      return
    }
    setSubmitting(true)
    setError(null)
    try {
      await login(identifier, password)
      navigate(location.state?.from?.pathname || '/', { replace: true })
    } catch (err) {
      setError(err)
      setSubmitting(false)
    }
  }

  return (
    <div className="login-page">
      <section className="login-panel" aria-hidden="true">
        <div className="row" style={{ fontWeight: 800, fontSize: 18 }}>
          <BookOpenCheck size={24} /> ThesisFormat
        </div>
        <BlobIllustration size={230} icon={ShieldCheck} blob="rgba(255,255,255,.22)" />
        <h2>Pantau dan validasi hasil pemeriksaan format karya tulis mahasiswa.</h2>
        <ul>
          {FEATURES.map(({ icon: Icon, text }) => (
            <li key={text}>
              <span>
                <Icon size={16} />
              </span>
              {text}
            </li>
          ))}
        </ul>
      </section>

      <section className="login-form-area">
        <form className="login-form" onSubmit={handleSubmit} noValidate>
          <div>
            <div className="brand-icon" style={{ marginBottom: 16 }}>
              <BookOpenCheck size={22} />
            </div>
            <h1>Masuk Dashboard</h1>
            <p className="muted" style={{ margin: '6px 0 0' }}>
              Khusus admin/staf ThesisFormat.
            </p>
          </div>

          <ErrorAlert error={error} />

          <div className="field">
            <label htmlFor="identifier">Email atau username</label>
            <div className="input-icon">
              <Mail size={18} />
              <input
                id="identifier"
                className="input"
                autoComplete="username"
                placeholder="admin@polinela.ac.id"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
              />
            </div>
          </div>

          <div className="field">
            <label htmlFor="password">Password</label>
            <div className="input-icon has-toggle">
              <Lock size={18} />
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                className="input"
                autoComplete="current-password"
                placeholder="Masukkan password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
              <button
                type="button"
                className="input-toggle"
                onClick={() => setShowPassword((show) => !show)}
                aria-label={showPassword ? 'Sembunyikan password' : 'Lihat password'}
                aria-pressed={showPassword}
                title={showPassword ? 'Sembunyikan password' : 'Lihat password'}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
          </div>

          <button type="submit" className="btn btn-block" disabled={submitting}>
            {submitting ? 'Memproses...' : 'Masuk'}
          </button>
        </form>
      </section>
    </div>
  )
}
