import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/features/auth/store/auth'

import LoginPage from '@/features/auth/pages/LoginPage.vue'
import RegisterPage from '@/features/auth/pages/RegisterPage.vue'
import OnboardingPage from '@/features/onboarding/pages/OnboardingPage.vue'
import OverviewPage from '@/features/overview/pages/OverviewPage.vue'
import OverviewPageNew from '@/features/overview/pages/OverviewPageNew.vue'
import ConsultPage from '@/features/consult/pages/ConsultPage.vue'
import HistoryPage from '@/features/history/pages/HistoryPage.vue'
import InsightsPage from '@/features/insights/pages/InsightsPage.vue'
import SettingsPage from '@/features/settings/pages/SettingsPage.vue'
import AdminPage from '@/features/admin/pages/AdminPage.vue'

const routes = [
  {
    path: '/auth/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresGuest: true }
  },
  {
    path: '/auth/register',
    name: 'Register',
    component: RegisterPage,
    meta: { requiresGuest: true }
  },
  {
    path: '/onboarding',
    name: 'Onboarding',
    component: OnboardingPage,
    meta: { requiresAuth: true, requiresOnboarding: false }
  },
  {
    path: '/app/overview',
    name: 'Overview',
    component: OverviewPage,
    meta: { requiresAuth: true, requiresOnboarding: true }
  },
  {
    path: '/app/overview-new',
    name: 'OverviewNew',
    component: OverviewPageNew,
    meta: { requiresAuth: true, requiresOnboarding: true }
  },
  {
    path: '/app/consult',
    name: 'Consult',
    component: ConsultPage,
    meta: { requiresAuth: true, requiresOnboarding: true }
  },
  {
    path: '/app/history',
    name: 'History',
    component: HistoryPage,
    meta: { requiresAuth: true, requiresOnboarding: true }
  },
  {
    path: '/app/insights',
    name: 'Insights',
    component: InsightsPage,
    meta: { requiresAuth: true, requiresOnboarding: true }
  },
  {
    path: '/app/settings',
    name: 'Settings',
    component: SettingsPage,
    meta: { requiresAuth: true, requiresOnboarding: true }
  },
  {
    path: '/app/admin',
    name: 'Admin',
    component: AdminPage,
    meta: { requiresAuth: true, requiresOnboarding: true, requiresAdmin: true }
  },
  // Redirect root to login
  {
    path: '/',
    redirect: '/auth/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Handle root path
  if (to.path === '/' && authStore.isAuthenticated) {
    if (!authStore.onboardingCompleted) {
      return next('/onboarding')
    }
    return next('/app/overview')
  }

  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    if (!authStore.onboardingCompleted) {
      return next('/onboarding')
    }
    return next('/app/overview')
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next('/auth/login')
  }

  if (to.meta.requiresOnboarding && !authStore.onboardingCompleted) {
    return next('/onboarding')
  }

  if (to.path === '/onboarding' && authStore.onboardingCompleted) {
    return next('/app/overview')
  }

  // Check admin permission
  if (to.meta.requiresAdmin) {
    if (!authStore.user) {
      try {
        await authStore.fetchUserOverview()
      } catch (err) {
        console.error('Failed to fetch user overview:', err)
        return next('/auth/login')
      }
    }

    if (!authStore.user?.is_admin) {
      console.warn('User is not admin, redirecting to overview')
      return next('/app/overview')
    }
  }

  next()
})

export default router
