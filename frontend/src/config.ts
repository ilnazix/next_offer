const DEFAULT_API_BASE_URL = 'http://localhost:8000'
const DEFAULT_CLIENT_ID = 1

function resolveApiBaseUrl(): string {
  const configured = import.meta.env.VITE_API_BASE_URL
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
