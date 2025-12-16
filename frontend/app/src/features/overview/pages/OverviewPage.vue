<template>
  <div class="min-h-screen bg-bg">
    <!-- Header -->
    <div class="py-6">
      <div class="max-w-[1400px] mx-auto lg:px-8 px-4 flex items-center justify-between">
        <!-- Left: Greeting -->
        <div>
          <h1 class="lg:text-3xl text-2xl font-bold font-serif text-textMain">
            Hello, <span class="text-primary">{{ authStore.user?.nickname || 'User' }}</span>
          </h1>
        </div>

        <!-- Right: Icons + User -->
        <div class="flex items-center space-x-4">
          <!-- Settings Icon -->
          <button
            @click="$router.push('/app/settings')"
            class="p-2 hover:bg-stone-100 rounded-full transition"
          >
            <svg class="w-6 h-6 text-textSub" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>

          <!-- Logout Icon -->
          <button
            @click="showLogoutModal = true"
            class="p-2 hover:bg-red-50 rounded-full transition"
            title="Log Out"
          >
            <svg class="w-6 h-6 text-textSub" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </button>

          <!-- User Avatar -->
          <div class="pl-3 border-l border-gray-200">
            <div class="w-10 h-10 rounded-full bg-primary flex items-center justify-center text-white font-semibold">
              {{ (authStore.user?.nickname || 'U')[0].toUpperCase() }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-[1400px] mx-auto lg:px-8 px-4 py-6">
      <!-- Grid 容器：桌面端3行等高，移动端单列堆叠 -->
      <div
        class="grid lg:grid-cols-12 grid-cols-1 lg:gap-6 gap-4 lg:grid-rows-[200px_200px_200px]"
      >

        <!-- ========== 左侧列 ========== -->

        <!-- Row 1: Action Buttons -->
        <div class="lg:col-span-3 lg:row-start-1 col-span-1 order-1 lg:order-none">
          <div class="space-y-3">
            <!-- 开始咨询 -->
            <button
              @click="$router.push('/app/consult')"
              class="w-full bg-gradient-to-br from-primary to-primary rounded-xl lg:p-4 p-3 shadow-sm hover:shadow-lg transition-all duration-200 group flex items-center justify-center space-x-3"
            >
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
              </svg>
              <span class="font-extrabold font-serif text-white">Start Consultation</span>
            </button>

            <!-- 过往咨询 -->
            <button
              @click="$router.push('/app/history')"
              class="w-full bg-gradient-to-br from-secondary to-secondary rounded-xl lg:p-4 p-3 shadow-sm hover:shadow-lg transition-all duration-200 group flex items-center justify-center space-x-3"
            >
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              <span class="font-extrabold font-serif text-white">Consultation History</span>
            </button>

            <!-- 整体回顾 -->
            <button
              @click="$router.push('/app/insights')"
              class="w-full bg-gradient-to-br from-tertiary to-tertiary rounded-xl lg:p-4 p-3 shadow-sm hover:shadow-lg transition-all duration-200 group flex items-center justify-center space-x-3"
            >
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <span class="font-extrabold font-serif text-white">Insights</span>
            </button>
          </div>
        </div>

        <!-- Row 2-3: 咨询日程（跨2行） -->
        <div class="lg:col-span-3 lg:row-start-2 lg:row-span-2 col-span-1 order-5 lg:order-none">
          <WeekCalendar class="h-full" />
        </div>

        <!-- ========== 中间列 ========== -->

        <!-- Row 1-2: 情绪指数（跨2行） -->
        <div class="lg:col-span-6 lg:row-start-1 lg:row-span-2 col-span-1 order-3 lg:order-none">
          <HealthReport class="h-full" />
        </div>

        <!-- Row 3: 咨询数据 -->
        <div class="lg:col-span-6 lg:row-start-3 col-span-1 order-4 lg:order-none">
          <DailyStats class="h-full" />
        </div>

        <!-- ========== 右侧列 ========== -->

        <!-- Row 1-2: 你的咨询师（跨2行） -->
        <div class="lg:col-span-3 lg:row-start-1 lg:row-span-2 col-span-1 order-2 lg:order-none">
          <YourTherapist class="h-full" />
        </div>

        <!-- Row 3: 积极心理 Tips -->
        <div class="lg:col-span-3 lg:row-start-3 col-span-1 order-6 lg:order-none">
          <PsychologyTips class="h-full" />
        </div>

      </div>
    </div>

    <!-- Logout Confirmation Modal -->
    <div
      v-if="showLogoutModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showLogoutModal = false"
    >
      <div class="bg-white rounded-lg shadow-xl p-6 max-w-md w-full mx-4">
        <h3 class="text-xl font-semibold font-serif text-textMain mb-4">Confirm Log Out</h3>
        <p class="text-textSub font-serif mb-6">Are you sure you want to log out?</p>
        <div class="flex justify-end space-x-3">
          <button
            @click="showLogoutModal = false"
            class="px-4 py-2 border border-gray-300 text-textMain font-serif rounded-lg hover:bg-gray-50 transition duration-200"
          >
            Cancel
          </button>
          <button
            @click="handleLogout"
            class="px-4 py-2 bg-red-600 text-white font-serif rounded-lg hover:bg-red-700 transition duration-200"
          >
            Log Out
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/features/auth/store/auth'
import WeekCalendar from '@/features/overview/components/WeekCalendar.vue'
import HealthReport from '@/features/overview/components/HealthReport.vue'
import DailyStats from '@/features/overview/components/DailyStats.vue'
import YourTherapist from '@/features/overview/components/YourTherapist.vue'
import PsychologyTips from '@/features/overview/components/PsychologyTips.vue'

const router = useRouter()
const authStore = useAuthStore()

const showLogoutModal = ref(false)

onMounted(() => {
  authStore.fetchUserOverview()
})

function handleLogout() {
  authStore.logout()
  router.push('/auth/login')
}
</script>
