const dateTime = new Intl.DateTimeFormat('id-ID', {
  dateStyle: 'medium',
  timeStyle: 'short',
})

const dateOnly = new Intl.DateTimeFormat('id-ID', { dateStyle: 'medium' })

const shortDate = new Intl.DateTimeFormat('id-ID', {
  day: 'numeric',
  month: 'short',
})

export const formatDateTime = (value) =>
  value ? dateTime.format(new Date(value)) : '-'

export const formatDate = (value) => (value ? dateOnly.format(new Date(value)) : '-')

export const formatShortDate = (value) =>
  value ? shortDate.format(new Date(value)) : '-'

export const formatNumber = (value, suffix = '') =>
  value === null || value === undefined
    ? '-'
    : `${Number(value).toLocaleString('id-ID')}${suffix}`
