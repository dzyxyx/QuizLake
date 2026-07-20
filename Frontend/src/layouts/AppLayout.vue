<script setup lang="ts">
import AppSidebar from '@/components/AppSidebar.vue'

withDefaults(
  defineProps<{
    activeItem?: 'active-quiz' | 'discover' | 'my-quizzes' | 'profile' | null
    activeDraftId?: number | null
  }>(),
  {
    activeItem: null,
    activeDraftId: null,
  },
)
</script>

<template>
  <div class="app-layout">
    <AppSidebar :active-item="activeItem" :active-draft-id="activeDraftId" />
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
