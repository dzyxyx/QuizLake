import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('@/views/RegisterView.vue'),
      meta: { guestOnly: true },
    },
    {
      path: '/join',
      name: 'join',
      component: () => import('@/views/JoinByCodeView.vue'),
    },
    {
      path: '/',
      name: 'dashboard',
      component: () => import('@/views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/discover',
      name: 'discover',
      component: () => import('@/views/DiscoverView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/quizzes/create',
      name: 'quiz-create-settings',
      component: () => import('@/views/CreateQuizSettingsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/quizzes/:id/edit',
      name: 'quiz-edit-settings',
      component: () => import('@/views/CreateQuizSettingsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/quizzes/:id/questions',
      name: 'quiz-add-questions',
      component: () => import('@/views/AddQuestionsView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/session/:code/waiting',
      name: 'session-waiting',
      component: () => import('@/views/WaitingRoomView.vue'),
    },
    {
      path: '/session/:code/live',
      name: 'session-live',
      component: () => import('@/views/LiveQuestionView.vue'),
    },
    {
      path: '/session/:code/results',
      name: 'session-results',
      component: () => import('@/views/ResultsView.vue'),
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/profile/edit',
      name: 'profile-edit',
      component: () => import('@/views/EditProfileView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach((to) => {
  const auth = useAuthStore()

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login' }
  }
  if (to.meta.guestOnly && auth.isAuthenticated) {
    return { name: 'dashboard' }
  }
})

export default router
