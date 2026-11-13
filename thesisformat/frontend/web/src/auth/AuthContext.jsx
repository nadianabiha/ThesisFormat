import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { clearSession, getSession, login as apiLogin } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => getSession()?.user ?? null)

  // Dipicu oleh api/client.js saat sesi tidak bisa diperpanjang.
  useEffect(() => {
    const onLogout = () => setUser(null)
    window.addEventListener('auth:logout', onLogout)
    return () => window.removeEventListener('auth:logout', onLogout)
  }, [])

  const login = useCallback(async (identifier, password) => {
    const loggedIn = await apiLogin(identifier, password)
    setUser(loggedIn)
    return loggedIn
  }, [])

  const logout = useCallback(() => {
    clearSession()
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
