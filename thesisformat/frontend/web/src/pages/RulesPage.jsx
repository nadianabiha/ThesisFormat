import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { BrainCircuit, Check, FlaskConical, Ruler, RotateCcw } from 'lucide-react'
import { getRules, updateRule } from '../api/dashboard'
import PageNav from '../components/PageNav'
import { ErrorAlert, Spinner } from '../components/ui'
import { formatDateTime } from '../utils/format'
import { useAsync } from '../utils/useAsync'

const MARGIN_LABELS = {
  top_margin: 'Atas',
  right_margin: 'Kanan',
  bottom_margin: 'Bawah',
  left_margin: 'Kiri',
}

const ALIGNMENT_LABELS = {
  LEFT: 'Rata kiri',
  CENTER: 'Rata tengah',
  RIGHT: 'Rata kanan',
  JUSTIFY: 'Rata kiri-kanan (justify)',
}

const SIZE_LABELS = {
  width_cm: 'Lebar',
  height_cm: 'Tinggi',
  tolerance_cm: 'Toleransi (±)',
}

const PAGE_GROUP_LABELS = {
  front: 'Halaman awal (kata pengantar, daftar isi, dll.)',
  body: 'Bagian isi (mulai Pendahuluan)',
}

const PAGE_OPTION_LABELS = {
  '': 'Tidak dicek',
  roman_lower: 'Romawi kecil (i, ii, iii)',
  roman_upper: 'Romawi besar (I, II, III)',
  arabic: 'Angka Arab (1, 2, 3)',
  top: 'Atas',
  bottom: 'Bawah',
  left: 'Kiri',
  center: 'Tengah',
  right: 'Kanan',
}

const COVER_LABELS = {
  logo: 'Logo Polinela',
  npm: 'Nama & NPM penulis',
  institusi: 'Nama institusi',
  tahun: 'Tahun',
}

const asObject = (value) => (value && typeof value === 'object' ? value : {})

function OptionSelect({ value, options, onChange, label }) {
  return (
    <label className="field margin-field">
      <span>{label}</span>
      <select className="select" value={value ?? ''} onChange={(e) => onChange(e.target.value)}>
        {options.map((option) => (
          <option key={option} value={option}>
            {PAGE_OPTION_LABELS[option] ?? option}
          </option>
        ))}
      </select>
    </label>
  )
}

function ValueInput({ rule, value, onChange }) {
  const spec = rule.input ?? { type: 'text' }
  const id = `value-${rule.id}`

  // Ukuran kertas / logo: lebar, tinggi, toleransi (cm).
  if (spec.type === 'size') {
    const size = asObject(value)
    return (
      <div className="margin-grid">
        {Object.entries(SIZE_LABELS).map(([key, label]) => (
          <label key={key} className="field margin-field">
            <span>
              {label} ({spec.unit})
            </span>
            <input
              type="number"
              className="input"
              min={key === 'tolerance_cm' ? 0 : spec.min}
              max={key === 'tolerance_cm' ? 5 : spec.max}
              step={0.1}
              value={size[key] ?? ''}
              onChange={(e) => onChange({ ...size, [key]: e.target.value })}
            />
          </label>
        ))}
      </div>
    )
  }

  // Nomor halaman: format, letak, posisi untuk halaman awal & bagian isi.
  if (spec.type === 'page_number') {
    const rules = asObject(value)
    const update = (group, key, next) =>
      onChange({ ...rules, [group]: { ...asObject(rules[group]), [key]: next } })
    return (
      <div className="stack" style={{ gap: 12 }}>
        {Object.entries(PAGE_GROUP_LABELS).map(([group, label]) => {
          const part = asObject(rules[group])
          return (
            <div key={group}>
              <div className="small muted" style={{ marginBottom: 6 }}>
                {label}
              </div>
              <div className="margin-grid">
                <OptionSelect
                  label="Format"
                  value={part.format}
                  options={spec.formats}
                  onChange={(next) => update(group, 'format', next)}
                />
                <OptionSelect
                  label="Letak"
                  value={part.vertical}
                  options={['', ...spec.verticals]}
                  onChange={(next) => update(group, 'vertical', next)}
                />
                <OptionSelect
                  label="Posisi"
                  value={part.horizontal}
                  options={['', ...spec.horizontals]}
                  onChange={(next) => update(group, 'horizontal', next)}
                />
              </div>
            </div>
          )
        })}
      </div>
    )
  }

  // Kelengkapan sampul: elemen wajib + nama institusi.
  if (spec.type === 'cover') {
    const cover = asObject(value)
    const required = Array.isArray(cover.required) ? cover.required : []
    const toggle = (key) =>
      onChange({
        ...cover,
        required: required.includes(key)
          ? required.filter((item) => item !== key)
          : spec.elements.filter((item) => item === key || required.includes(item)),
      })
    return (
      <div className="stack" style={{ gap: 10 }}>
        <div className="row" style={{ gap: 16 }}>
          {spec.elements.map((key) => (
            <label key={key} className="row small" style={{ gap: 6, flexWrap: 'nowrap' }}>
              <input type="checkbox" checked={required.includes(key)} onChange={() => toggle(key)} />
              {COVER_LABELS[key] ?? key}
            </label>
          ))}
        </div>
        {required.includes('institusi') && (
          <label className="field">
            <span>Nama institusi yang harus ada di sampul</span>
            <input
              className="input"
              value={cover.institution ?? ''}
              onChange={(e) => onChange({ ...cover, institution: e.target.value })}
            />
          </label>
        )}
      </div>
    )
  }

  if (spec.type === 'select') {
    return (
      <select id={id} className="select" value={value ?? ''} onChange={(e) => onChange(e.target.value)}>
        {spec.options.map((option) => (
          <option key={option} value={option}>
            {ALIGNMENT_LABELS[option] ?? option}
          </option>
        ))}
      </select>
    )
  }

  if (spec.type === 'margin') {
    const margins = value && typeof value === 'object' ? value : {}
    return (
      <div className="margin-grid">
        {Object.entries(MARGIN_LABELS).map(([key, label]) => (
          <label key={key} className="field margin-field">
            <span>{label}</span>
            <input
              type="number"
              className="input"
              min={spec.min}
              max={spec.max}
              step={0.1}
              value={margins[key] ?? ''}
              onChange={(e) => onChange({ ...margins, [key]: e.target.value })}
            />
          </label>
        ))}
      </div>
    )
  }

  return (
    <div className="row" style={{ flexWrap: 'nowrap' }}>
      <input
        id={id}
        className="input"
        type={spec.type === 'number' ? 'number' : 'text'}
        min={spec.min}
        max={spec.max}
        step={spec.step}
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value)}
      />
      {spec.unit && <span className="small muted">{spec.unit}</span>}
    </div>
  )
}

function RuleCard({ rule, onSaved }) {
  const semantic = rule.category === 'semantic'
  const original = semantic ? rule.instruction : rule.value
  const [draft, setDraft] = useState(original)
  const [note, setNote] = useState('')
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [savedVersion, setSavedVersion] = useState(null)

  useEffect(() => setDraft(semantic ? rule.instruction : rule.value), [rule, semantic])

  const dirty = JSON.stringify(draft) !== JSON.stringify(original)

  async function save(body) {
    setSaving(true)
    setError(null)
    try {
      const result = await updateRule(rule.id, { ...body, note: note.trim() || undefined })
      setSavedVersion(result.version)
      setNote('')
      onSaved(result.rule)
    } catch (err) {
      setError(err)
    } finally {
      setSaving(false)
    }
  }

  const anchor = `${rule.category}-${rule.rule_key}`

  return (
    <section id={anchor} className={`card rule-card${rule.active ? '' : ' inactive'}`}>
      <div className="card-title" style={{ alignItems: 'flex-start' }}>
        <div>
          <h2>{rule.label}</h2>
          <p>
            {rule.document_type_label}
            {rule.updated_at && ` · diubah ${formatDateTime(rule.updated_at)}`}
          </p>
        </div>
        <label className="switch" title={rule.active ? 'Nonaktifkan' : 'Aktifkan'}>
          <input
            type="checkbox"
            checked={rule.active}
            disabled={saving}
            onChange={(e) => save({ active: e.target.checked })}
          />
          <span className="switch-track" aria-hidden="true" />
          <span className="small">{rule.active ? 'Aktif' : 'Nonaktif'}</span>
        </label>
      </div>

      <div className="stack">
        {semantic ? (
          <div className="field">
            <label htmlFor={`instruction-${rule.id}`}>Instruksi untuk AI</label>
            <textarea
              id={`instruction-${rule.id}`}
              className="textarea"
              rows={4}
              maxLength={3000}
              value={draft ?? ''}
              onChange={(e) => setDraft(e.target.value)}
            />
            {rule.default_instruction && draft !== rule.default_instruction && (
              <button
                type="button"
                className="btn btn-ghost btn-sm"
                style={{ alignSelf: 'flex-start' }}
                onClick={() => setDraft(rule.default_instruction)}
              >
                <RotateCcw size={14} /> Kembalikan ke instruksi bawaan
              </button>
            )}
          </div>
        ) : (
          <div className="field">
            <label htmlFor={`value-${rule.id}`}>
              Nilai yang benar{rule.input?.type === 'margin' && ' (cm)'}
            </label>
            <ValueInput rule={rule} value={draft} onChange={setDraft} />
          </div>
        )}

        {dirty && (
          <div className="field">
            <label htmlFor={`note-${rule.id}`} className="small">
              Alasan perubahan (opsional, tercatat di riwayat versi)
            </label>
            <input
              id={`note-${rule.id}`}
              className="input"
              maxLength={255}
              placeholder="Mis. AI sering salah menilai abstrak yang sudah ≤ 250 kata"
              value={note}
              onChange={(e) => setNote(e.target.value)}
            />
          </div>
        )}

        <ErrorAlert error={error} />

        {savedVersion && !dirty && (
          <div className="alert alert-success" role="status">
            <Check size={18} />
            <div>
              Tersimpan sebagai <strong>versi {savedVersion}</strong>.{' '}
              <Link to="/ai-performance">Uji ulang di halaman Kinerja AI</Link> untuk melihat dampaknya.
            </div>
          </div>
        )}

        {dirty && (
          <div className="row">
            <button
              type="button"
              className="btn btn-sm"
              disabled={saving}
              onClick={() => save(semantic ? { instruction: draft } : { value: draft })}
            >
              {saving ? 'Menyimpan…' : 'Simpan perubahan'}
            </button>
            <button type="button" className="btn btn-ghost btn-sm" disabled={saving} onClick={() => setDraft(original)}>
              Batal
            </button>
          </div>
        )}
      </div>
    </section>
  )
}

export default function RulesPage() {
  const location = useLocation()
  const { data, loading, error, reload, setData } = useAsync(() => getRules(), [])

  // Buka langsung aturan yang dipilih dari halaman Kinerja AI (#semantic-abstrak).
  useEffect(() => {
    if (!data || !location.hash) return
    const target = document.getElementById(location.hash.slice(1))
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'center' })
      target.classList.add('highlight')
      const timer = setTimeout(() => target.classList.remove('highlight'), 2000)
      return () => clearTimeout(timer)
    }
    return undefined
  }, [data, location.hash])

  if (!data && loading) return <Spinner />
  if (!data && error) return <ErrorAlert error={error} onRetry={reload} />

  function replaceRule(updated) {
    setData({
      ...data,
      current_version: data.current_version + 1,
      [updated.category]: data[updated.category].map((r) => (r.id === updated.id ? updated : r)),
    })
  }

  return (
    <>
      <PageNav label="Kinerja AI" fallback="/ai-performance" />

      <div className="page-header">
        <div>
          <h1>Aturan &amp; Instruksi AI</h1>
          <p>
            Perbaiki aturan saat menemukan pola kesalahan AI. Setiap perubahan tercatat sebagai versi baru
            (sekarang <strong>versi {data.current_version}</strong>) dan langsung dipakai untuk unggahan
            berikutnya.
          </p>
        </div>
        <Link to="/ai-performance" className="btn btn-ghost">
          <FlaskConical size={16} /> Uji ulang di Kinerja AI
        </Link>
      </div>

      <div className="section-title">
        <div>
          <h2 className="row">
            <BrainCircuit size={20} color="var(--warning-strong)" /> Instruksi AI per aspek (Jalur B, bobot
            60%)
          </h2>
          <p>
            Instruksi ini dikirim ke Gemini. Perjelas aturan yang sering disalahpahami AI, atau nonaktifkan
            aspek yang terlalu sering keliru.
          </p>
        </div>
      </div>
      <div className="rules-grid">
        {data.semantic.map((rule) => (
          <RuleCard key={rule.id} rule={rule} onSaved={replaceRule} />
        ))}
      </div>

      <div className="section-title" style={{ marginTop: 26 }}>
        <div>
          <h2 className="row">
            <Ruler size={20} color="var(--primary)" /> Aturan format fisik (Jalur A, bobot 40%)
          </h2>
          <p>Nilai yang dianggap benar saat memeriksa font, ukuran, perataan, spasi, dan margin.</p>
        </div>
      </div>
      <div className="rules-grid">
        {data.physical.map((rule) => (
          <RuleCard key={rule.id} rule={rule} onSaved={replaceRule} />
        ))}
      </div>
    </>
  )
}
