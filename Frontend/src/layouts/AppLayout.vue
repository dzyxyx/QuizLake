<script setup lang="ts">
import AppSidebar from '@/components/AppSidebar.vue'

// Общий каркас "внутренних" страниц: сайдбар слева + область контента справа.
// Пропсы прокидываются в AppSidebar, чтобы каждая страница могла указать,
// какой пункт меню подсветить.
withDefaults(
  defineProps<{
    activeItem?: 'active-quiz' | 'discover' | 'my-quizzes' | 'profile' | null
    hasActiveSession?: boolean
    activeDraftId?: number | null
    showHistory?: boolean
  }>(),
  {
    activeItem: null,
    hasActiveSession: true,
    activeDraftId: null,
    showHistory: false,
  },
)
</script>

<template>
  <div class="app-layout">
    <AppSidebar
      :active-item="activeItem"
      :has-active-session="hasActiveSession"
      :active-draft-id="activeDraftId"
      :show-history="showHistory"
    />
    <main class="content">
      <slot />
    </main>
  </div>
</template>

<style scoped>
.app-layout {
  display: flex;
  align-items: stretch;
  min-height: 100vh;
}
.content {
  flex: 1;
  padding: 40px 48px;
  min-width: 0;
}
</style>
