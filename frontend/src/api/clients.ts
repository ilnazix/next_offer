import { config } from '../config'
import type { Client, ClientsResponse } from '../types'

export async function fetchClients(signal?: AbortSignal): Promise<Client[]> {
  const response = await fetch(`${config.apiBaseUrl}/api/v1/clients`, {
    headers: { Accept: 'application/json' },
    signal,
  })

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`)
  }

  const body = (await response.json()) as ClientsResponse
  return Array.isArray(body?.clients) ? body.clients : []
}
