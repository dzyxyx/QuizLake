<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/layouts/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import { ApiError } from '@/api/client'

const router = useRouter()
const auth = useAuthStore()

const firstName = ref(auth.user?.first_name ?? '')
const lastName = ref(auth.user?.last_name ?? '')
const nickname = ref(auth.user?.nickname ?? '')
const email = ref(auth.user?.email ?? '')
const newPassword = ref('')
const confirmPassword = ref('')
const error = ref('')
const saving = ref(false)

const initials = `${firstName.value[0] ?? ''}${lastName.value[0] ?? ''}`.toUpperCase()

async function onSave() {
  error.value = ''
  if (newPassword.value && newPassword.value !== confirmPassword.value) {
    error.value = 'Пароли не совпадают'
    return
  }

  saving.value = true
  try {
    await auth.updateProfile({
      first_name: firstName.value,
      last_name: lastName.value,
      nickname: nickname.value,
      email: email.value,
      password: newPassword.value || undefined,
    })
    router.push({ name: 'profile' })
  } catch (e) {
    error.value = e instanceof ApiError ? e.message : 'Не удалось сохранить изменения'
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <AppLayout active-item="profile">
    <RouterLink to="/profile" class="back-link">← Профиль</RouterLink>
    <h1 class="page-title">Редактирование профиля</h1>

    <div class="layout-row">
      <div class="card photo-card">
        <div class="section-label">Фото профиля</div>
        <div class="avatar-wrap">
          <span class="avatar-big">{{ initials }}</span>
          <span class="camera-badge">📷</span>
        </div>
        <p class="hint">Загрузка фото профиля пока не поддерживается</p>
      </div>

      <div class="card form-card">
        <form class="form" @submit.prevent="onSave">
          <div class="section-label">Основная информация</div>

          <div class="row-2">
            <div class="field">
              <label>Имя</label>
              <input v-model="firstName" type="text" />
            </div>
            <div class="field">
              <label>Фамилия</label>
              <input v-model="lastName" type="text" />
            </div>
          </div>

          <div class="field">
            <label>Псевдоним (виден другим участникам в игре)</label>
            <input v-model="nickname" type="text" />
            <p class="field-hint">
              Используется вместо имени в комнате ожидания, во время квиза и в таблице результатов
            </p>
          </div>

          <div class="field">
            <label>Email</label>
            <input v-model="email" type="email" />
          </div>

          <div class="divider" />

          <div class="section-label">Смена пароля</div>
          <div class="row-2">
            <div class="field">
              <label>Новый пароль</label>
              <input
                v-model="newPassword"
                type="password"
                placeholder="Оставьте пустым, если не меняете"
              />
            </div>
            <div class="field">
              <label>Подтверждение пароля</label>
              <input
                v-model="confirmPassword"
                type="password"
                placeholder="Повторите новый пароль"
              />
            </div>
          </div>

          <p v-if="error" class="error-text">{{ error }}</p>

          <div class="actions">
            <RouterLink to="/profile" class="btn btn-secondary">Отмена</RouterLink>
            <button type="submit" class="btn btn-primary" :disabled="saving">
              {{ saving ? 'Сохраняем…' : 'СОХРАНИТЬ ИЗМЕНЕНИЯ' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </AppLayout>
</template>

<style scoped>
.back-link {
  font-size: 13px;
  font-weight: 600;
  color: var(--color-primary);
  display: inline-block;
  margin-bottom: 8px;
}
.page-title {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 24px;
}

.layout-row {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.photo-card {
  width: 260px;
  flex-shrink: 0;
  padding: 28px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.avatar-wrap {
  position: relative;
  margin: 8px 0 4px;
}
.avatar-big {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
}
.camera-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: #fff;
  border: 2px solid var(--color-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
}
.hint {
  font-size: 12px;
  color: var(--color-text-secondary);
  text-align: center;
}

.form-card {
  flex: 1;
  padding: 32px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.section-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}
.row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.field-hint {
  font-size: 12px;
  color: var(--color-text-secondary);
}
.divider {
  border-top: 1px solid var(--color-border);
  margin: 4px 0;
}
.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 8px;
}
.error-text {
  font-size: 13px;
  color: var(--color-danger-text);
}
</style>
