import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

/** Halaman yang hanya boleh dibuka admin yang sudah login. */
export default function ProtectedRoute({ children }) {
  const { user } = useAuth()
  const location = useLocation()

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />
  }
  return children
}
