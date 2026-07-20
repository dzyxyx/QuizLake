import { apiRequest } from '@/api/client'
import type { Category } from '@/types'

export function listCategories() {
  return apiRequest<Category[]>('/categories', { auth: false })
}
