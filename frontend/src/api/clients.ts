import type { Client, ClientsResponse } from '../types'
import { fetchJson } from './http'

export async function fetchClients(signal?: AbortSignal): Promise<Client[]> {
  const body = await fetchJson<ClientsResponse>('/api/v1/clients', { signal })
  return Array.isArray(body?.clients) ? body.clients : []
}
