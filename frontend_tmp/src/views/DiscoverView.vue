<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import PublicQuizCard from '@/components/PublicQuizCard.vue'
import { useDiscoverStore } from '@/stores/discover'
import { useCategoriesStore } from '@/stores/categories'
import { useAuthStore } from '@/stores/auth'
import { useSessionStore } from '@/stores/session'
import { ApiError } from '@/api/client'

const router = useRouter()
const discover = useDiscoverStore()
const categoriesStore = useCategoriesStore()
const auth = useAuthStore()
const sessionStore = useSessionStore()

const search = ref('')
const category = ref('Все категории')
const error = ref('')

onMounted(() => {
  discover.fetchSessions()
  categoriesStore.fetchCategories()
})

const filtered = computed(() =>
  discover.sessions.filter((s) => {
    const matchesCategory = category.value === 'Все категории' || s.category_name === category.value
    const query = search.value.trim().toLowerCase()
    const matchesSearch =
      !query || s.title.toLowerCase().includes(query) || s.owner_nickname.toLowerCase().includes(query)
    return matchesCategory && matchesSearch
  }),
)

async function onJoin(roomCode: string) {
  error.value = ''
  try {
    await sessionStore.loadByRoomCode(roomCode)
    await sessionStore.join(roomCode, auth.user!.nickname)
    router.push({ name: 'session-waiting', params: { code: roomCode } })
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось присоединиться к комнате'
  }
}
</script>

<template>
  <AppLayout active-item="discover">
    <header class="page-header">
      <h1>Публичные квизы</h1>
      <p class="subtitle">Присоединяйтесь к квизам, которые сейчас идут или скоро начнутся</p>
    </header>

    <div class="filters">
      <input
        v-model="search"
        type="text"
        class="search-input"
        placeholder="Найти квиз или организатора"
      />
      <select v-model="category" class="category-select">
        <option>Все категории</option>
        <option v-for="c in categoriesStore.categories" :key="c.id" :value="c.name">{{ c.name }}</option>
      </select>
      <RouterLink to="/join" class="btn btn-secondary">🔑 Войти по коду</RouterLink>
    </div>

    <p v-if="error" class="error-text">{{ error }}</p>

    <section v-if="filtered.length" class="quiz-grid">
      <PublicQuizCard v-for="s in filtered" :key="s.session_id" :session="s" @join="onJoin" />
    </section>
    <p v-else class="empty-hint">Сейчас нет доступных публичных квизов.</p>
  </AppLayout>
</template>

<style scoped>
.page-header {
  margin-bottom: 24px;
}
.page-header h1 {
  font-size: 24px;
  font-weight: 700;
}
.subtitle {
  color: var(--color-text-secondary);
  font-size: 13px;
  margin-top: 6px;
}

.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 28px;
}
.search-input {
  flex: 1;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  font-size: 14px;
  outline: none;
  background: #fff;
}
.search-input:focus {
  border-color: var(--color-primary);
}
.category-select {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 12px 14px;
  font-size: 14px;
  background: #fff;
  outline: none;
  min-width: 180px;
}

.quiz-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}
.empty-hint {
  color: var(--color-text-secondary);
  font-size: 14px;
}
.error-text {
  font-size: 13px;
  color: var(--color-danger-text);
  margin-bottom: 16px;
}
</style>
