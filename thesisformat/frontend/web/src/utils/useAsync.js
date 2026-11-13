import { useCallback, useEffect, useRef, useState } from 'react'

/**
 * Menjalankan fungsi async (mis. panggilan API) dan menyimpan
 * status loading / data / error. Panggil ulang lewat `reload()`.
 */
export function useAsync(fn, deps) {
  const [state, setState] = useState({ loading: true, data: null, error: null })
  const latest = useRef(0)

  const run = useCallback(() => {
    const id = ++latest.current
    setState((prev) => ({ ...prev, loading: true, error: null }))
    fn()
      .then((data) => {
        if (id === latest.current) setState({ loading: false, data, error: null })
      })
      .catch((error) => {
        if (id === latest.current) setState((prev) => ({ ...prev, loading: false, error }))
      })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => {
    run()
  }, [run])

  return { ...state, reload: run, setData: (data) => setState((s) => ({ ...s, data })) }
}
