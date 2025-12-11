import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from '@/api/axios'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const user = ref(null)
  const onboardingCompleted = ref(localStorage.getItem('onboarding_completed') === 'true')

  const isAuthenticated = computed(() => !!token.value)

  function setToken(newToken) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem('token', newToken)
    } else {
      localStorage.removeItem('token')
    }
  }

  function setUser(userData) {
    user.value = userData
  }

  function setOnboardingCompleted(completed) {
    onboardingCompleted.value = completed
    if (completed) {
      localStorage.setItem('onboarding_completed', 'true')
    } else {
      localStorage.removeItem('onboarding_completed')
    }
  }

  function logout() {
    token.value = null
    user.value = null
    onboardingCompleted.value = false
    localStorage.removeItem('token')
    localStorage.removeItem('onboarding_completed')
  }

  async function fetchUserOverview() {
    if (!token.value) return

    try {
      const resp = await axios.get('/api/me/overview')
      user.value = resp.data
      setOnboardingCompleted(resp.data.has_finished_onboarding)
    } catch (e) {
      console.error('Failed to fetch user overview:', e)
    }
  }

  return {
    token,
    user,
    onboardingCompleted,
    isAuthenticated,
    setToken,
    setUser,
    setOnboardingCompleted,
    logout,
    fetchUserOverview
  }
})
