export interface ABCItem {
  supplier_article: string
  nm_id: number
  barcode: string
  subject: string
  brand: string
  category: "A" | "B" | "C"
  orders_count: number
  revenue: number
  revenue_share: number
  cumulative_share: number
}
