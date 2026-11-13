import { config } from '../config'

export async function fetchJson<T>(
  path: string,
  { body, ...init }: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers)
  headers.set('Accept', 'application/json')
  if (body !== undefined && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(`${config.apiBaseUrl}${path}`, {
    ...init,
    headers,
    body,
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  return (await response.json()) as T
}

export function describeError(cause: unknown): string {
  return cause instanceof Error ? cause.message : 'unknown error'
}

export function isAbortError(cause: unknown): boolean {
  return cause instanceof Error && cause.name === 'AbortError'
}
