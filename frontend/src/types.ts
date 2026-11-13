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

export type OfferAction = 'accepted' | 'declined' | 'dismissed'

export interface FeedbackResponse {
  id: number
  status: OfferAction
  responded_at: string
}
