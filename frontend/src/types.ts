export interface Offer {
  id: number
  type: string
  title: string
  subtitle: string | null
  background_color: string | null
  icon: string | null
  action_text: string | null
  status: string
  created_at: string | null
}

export interface OffersResponse {
  client_id: number
  offers: Offer[]
}

export interface Client {
  id: number
  full_name: string | null
}

export interface ClientsResponse {
  clients: Client[]
}

export interface EventAccepted {
  event_id: string
  status: string
}
