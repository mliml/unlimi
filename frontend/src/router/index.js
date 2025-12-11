import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

import LandingPage from '@/pages/LandingPage.vue'
import LoginPage from '@/pages/LoginPage.vue'
import RegisterPage from '@/pages/RegisterPage.vue'
import OnboardingPage from '@/pages/OnboardingPage.vue'
import OverviewPage from '@/pages/OverviewPage.vue'
import OverviewPageNew from '@/pages/OverviewPageNew.vue'
import ConsultPage from '@/pages/ConsultPage.vue'
import HistoryPage from '@/pages/HistoryPage.vue'
import InsightsPage from '@/pages/InsightsPage.vue'
import SettingsPage from '@/pages/SettingsPage.vue'
import AdminPage from '@/pages/AdminPage.vue'

const routes = [
  {
    path: '/',
    name: 'Landing',
    component: LandingPage,
    meta: { isPublic: true }
  },
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
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Handle authenticated users visiting landing page
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

  // 检查是否需要 Admin 权限
  if (to.meta.requiresAdmin) {
    // 如果用户信息未加载，先加载
    if (!authStore.user) {
      try {
        await authStore.fetchUserOverview()
      } catch (err) {
        console.error('Failed to fetch user overview:', err)
        return next('/auth/login')
      }
    }

    // 检查是否为管理员
    if (!authStore.user?.is_admin) {
      console.warn('User is not admin, redirecting to overview')
      return next('/app/overview')
    }
  }

  next()
})

export default router
