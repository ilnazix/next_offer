const DEFAULT_API_BASE_URL = 'http://localhost:8000'
const DEFAULT_CLIENT_ID = 1
const SAME_ORIGIN_MARKER = 'same-origin'

function resolveApiBaseUrl(): string {
  const configured = import.meta.env.VITE_API_BASE_URL

  // When the UI and API are served from the same host (VPS + Caddy),
  // requests must be relative so the browser uses the current origin.
  if (configured === SAME_ORIGIN_MARKER) {
    return ''
  }

  return (configured && configured.trim() ? configured : DEFAULT_API_BASE_URL).replace(
    /\/+$/,
    '',
  )
}

function resolveClientId(): number {
  const configured = Number(import.meta.env.VITE_CLIENT_ID)
  return Number.isInteger(configured) && configured > 0 ? configured : DEFAULT_CLIENT_ID
}

export const config = {
  apiBaseUrl: resolveApiBaseUrl(),
  clientId: resolveClientId(),
  pollingIntervalMs: 3000,
  toastTimeoutMs: 8000,
} as const
