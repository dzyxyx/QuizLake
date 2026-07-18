<script setup lang="ts">
// Каркас для страниц входа/регистрации/входа по коду: слева синяя панель
// с заголовком и описанием (передаются через пропсы), справа — форма (slot).
defineProps<{
  heading: string
  description?: string
}>()
</script>

<template>
  <div class="auth-layout">
    <aside class="side-panel">
      <div class="logo">
        <span class="logo-dot" />
        <span class="logo-text">QuizLake</span>
      </div>

      <div class="side-content">
        <h1>{{ heading }}</h1>
        <p v-if="description">{{ description }}</p>
        <slot name="side-extra" />
      </div>
    </aside>

    <section class="form-panel">
      <slot name="top-right" />
      <div class="form-wrap">
        <slot />
      </div>
    </section>
  </div>
</template>

<style scoped>
.auth-layout {
  display: flex;
  min-height: 100vh;
}

.side-panel {
  width: 45%;
  min-width: 380px;
  background: var(--color-primary-gradient);
  color: #fff;
  padding: 40px;
  display: flex;
  flex-direction: column;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}
.logo-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #fff;
}
.logo-text {
  font-size: 18px;
  font-weight: 700;
}

.side-content {
  margin-top: auto;
  margin-bottom: auto;
  max-width: 380px;
}
.side-content h1 {
  font-size: 32px;
  font-weight: 700;
  line-height: 1.25;
  margin-bottom: 16px;
}
.side-content p {
  font-size: 15px;
  opacity: 0.85;
  line-height: 1.5;
}

.form-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 40px;
}

.form-wrap {
  width: 100%;
  max-width: 380px;
}
</style>
