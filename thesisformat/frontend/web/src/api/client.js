// Klien API untuk backend Django.
// - Menyimpan sesi (token JWT) di localStorage.
// - Jika access token kedaluwarsa (401), otomatis minta token baru
//   memakai refresh token, lalu mengulang permintaan.

export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
).replace(/\/$/, '')

const SESSION_KEY = 'thesisformat_admin_session'

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message)
    this.status = status
    this.data = data
  }
}

export function getSession() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY))
  } catch {
    return null
  }
}

function setSession(session) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session))
}

export function clearSession() {
  localStorage.removeItem(SESSION_KEY)
}

// Ubah respons error Django/DRF menjadi pesan yang mudah dibaca.
function messageFrom(data, status) {
  if (data && typeof data === 'object') {
    if (typeof data.detail === 'string') return data.detail
    const parts = Object.entries(data).map(([field, value]) => {
      const text = Array.isArray(value) ? value.join(' ') : String(value)
      return field === 'non_field_errors' ? text : `${field}: ${text}`
    })
    if (parts.length) return parts.join('\n')
  }
  if (status === 403) return 'Akses ditolak. Akun ini bukan admin.'
  if (status >= 500) return `Server sedang bermasalah (HTTP ${status}).`
  return `Permintaan gagal (HTTP ${status}).`
}

async function request(path, { method = 'GET', body, params, token } = {}) {
  const url = new URL(API_BASE_URL + path)
  Object.entries(params || {}).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      url.searchParams.set(key, value)
    }
  })

  const headers = { Accept: 'application/json' }
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers.Authorization = `Bearer ${token}`

  let response
  try {
    response = await fetch(url, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    })
  } catch {
    throw new ApiError(
      `Tidak dapat terhubung ke backend (${API_BASE_URL}). Pastikan server Django berjalan.`,
      0,
      null,
    )
  }

  const data = await response.json().catch(() => null)
  return { response, data }
}

let refreshing = null

async function refreshAccessToken() {
  const session = getSession()
  if (!session?.refresh) return false
  const { response, data } = await request('/api/token/refresh/', {
    method: 'POST',
    body: { refresh: session.refresh },
  })
  if (!response.ok || !data?.access) return false
  setSession({ ...session, access: data.access })
  return true
}

function forceLogout() {
  clearSession()
  window.dispatchEvent(new Event('auth:logout'))
}

/** Panggil endpoint yang butuh login admin. */
export async function api(path, options = {}) {
  let { response, data } = await request(path, {
    ...options,
    token: getSession()?.access,
  })

  if (response.status === 401) {
    refreshing ??= refreshAccessToken().finally(() => {
      refreshing = null
    })
    if (await refreshing) {
      ;({ response, data } = await request(path, {
        ...options,
        token: getSession()?.access,
      }))
    } else {
      forceLogout()
      throw new ApiError('Sesi berakhir. Silakan login kembali.', 401, data)
    }
  }

  if (!response.ok) {
    throw new ApiError(messageFrom(data, response.status), response.status, data)
  }
  return data
}

/** Login admin. Akun non-staf ditolak. */
export async function login(identifier, password) {
  const value = identifier.trim()
  const { response, data } = await request('/api/token/', {
    method: 'POST',
    body: {
      // Akun mahasiswa memakai email sebagai username (huruf kecil).
      username: value.includes('@') ? value.toLowerCase() : value,
      password,
    },
  })

  if (!response.ok) {
    const message =
      response.status === 401
        ? 'Email/username atau password salah.'
        : messageFrom(data, response.status)
    throw new ApiError(message, response.status, data)
  }

  if (!data?.user?.is_staff) {
    throw new ApiError(
      'Akun ini bukan admin. Dashboard hanya untuk admin/staf.',
      403,
      data,
    )
  }

  const session = { access: data.access, refresh: data.refresh, user: data.user }
  setSession(session)
  return session.user
}
