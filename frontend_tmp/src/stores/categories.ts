import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Category } from '@/types'
import * as categoriesApi from '@/api/categories'

export const useCategoriesStore = defineStore('categories', () => {
  const categories = ref<Category[]>([])
  const loaded = ref(false)

  async function fetchCategories(force = false) {
    if (loaded.value && !force) return
    categories.value = await categoriesApi.listCategories()
    loaded.value = true
  }

  return { categories, fetchCategories }
})
