<template>
  <div class="bg-white rounded-2xl p-6 shadow-sm">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h3 class="font-semibold text-gray-800 flex items-center">
        <svg class="w-5 h-5 mr-2 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" />
        </svg>
        活动趋势
      </h3>
      <div class="flex items-center space-x-2">
        <button class="text-xs px-3 py-1 rounded-lg bg-purple-100 text-purple-700 font-medium">
          本周
        </button>
        <button class="text-xs px-3 py-1 rounded-lg text-gray-600 hover:bg-gray-100 font-medium transition">
          本月
        </button>
      </div>
    </div>

    <!-- Legend -->
    <div class="flex items-center space-x-4 mb-4">
      <div class="flex items-center">
        <div class="w-3 h-3 rounded-full bg-purple-500 mr-2"></div>
        <span class="text-xs text-gray-600">咨询时长</span>
      </div>
      <div class="flex items-center">
        <div class="w-3 h-3 rounded-full bg-blue-400 mr-2"></div>
        <span class="text-xs text-gray-600">完成任务</span>
      </div>
      <div class="flex items-center">
        <div class="w-3 h-3 rounded-full bg-orange-400 mr-2"></div>
        <span class="text-xs text-gray-600">情绪记录</span>
      </div>
    </div>

    <!-- Chart -->
    <div class="relative">
      <!-- Y-axis labels -->
      <div class="absolute left-0 top-0 bottom-6 flex flex-col justify-between text-xs text-gray-400">
        <span>100</span>
        <span>75</span>
        <span>50</span>
        <span>25</span>
        <span>0</span>
      </div>

      <!-- Chart area -->
      <div class="ml-8 pl-2 border-l border-b border-gray-200">
        <div class="flex items-end justify-between h-48 pb-4">
          <div
            v-for="day in chartData"
            :key="day.day"
            class="flex-1 flex flex-col items-center group"
          >
            <!-- Bars container -->
            <div class="relative w-full flex items-end justify-center space-x-1 h-full px-2">
              <!-- Consultation bar -->
              <div
                class="relative w-full max-w-[20px] bg-gradient-to-t from-purple-600 to-purple-400 rounded-t-lg transition-all duration-300 group-hover:opacity-80 cursor-pointer"
                :style="{ height: `${(day.consultation / 100) * 100}%` }"
              >
                <div class="absolute -top-6 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-gray-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                  {{ day.consultation }}min
                </div>
              </div>

              <!-- Tasks bar -->
              <div
                class="relative w-full max-w-[20px] bg-gradient-to-t from-blue-500 to-blue-300 rounded-t-lg transition-all duration-300 group-hover:opacity-80 cursor-pointer"
                :style="{ height: `${(day.tasks / 20) * 100}%` }"
              >
                <div class="absolute -top-6 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-gray-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                  {{ day.tasks }}个
                </div>
              </div>

              <!-- Mood bar -->
              <div
                class="relative w-full max-w-[20px] bg-gradient-to-t from-orange-500 to-orange-300 rounded-t-lg transition-all duration-300 group-hover:opacity-80 cursor-pointer"
                :style="{ height: `${(day.mood / 15) * 100}%` }"
              >
                <div class="absolute -top-6 left-1/2 transform -translate-x-1/2 opacity-0 group-hover:opacity-100 transition-opacity bg-gray-800 text-white text-xs px-2 py-1 rounded whitespace-nowrap">
                  {{ day.mood }}次
                </div>
              </div>
            </div>

            <!-- Day label -->
            <span class="text-xs text-gray-600 font-medium mt-2">{{ day.day }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary -->
    <div class="mt-6 pt-4 border-t border-gray-100 flex items-center justify-between">
      <div class="text-sm text-gray-600">
        <span class="font-semibold text-purple-600">本周总计:</span>
        <span class="ml-2">咨询 {{ weekTotal.consultation }}min</span>
        <span class="mx-2">•</span>
        <span>任务 {{ weekTotal.tasks }}个</span>
        <span class="mx-2">•</span>
        <span>记录 {{ weekTotal.mood }}次</span>
      </div>
      <button class="text-xs text-purple-600 hover:text-purple-700 font-medium transition">
        导出报告 →
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

// Mock chart data
const chartData = [
  { day: '周一', consultation: 45, tasks: 8, mood: 5 },
  { day: '周二', consultation: 60, tasks: 12, mood: 7 },
  { day: '周三', consultation: 30, tasks: 6, mood: 4 },
  { day: '周四', consultation: 75, tasks: 15, mood: 9 },
  { day: '周五', consultation: 50, tasks: 10, mood: 6 },
  { day: '周六', consultation: 40, tasks: 7, mood: 5 },
  { day: '周日', consultation: 35, tasks: 5, mood: 3 }
]

// Calculate week totals
const weekTotal = computed(() => {
  return chartData.reduce(
    (acc, day) => ({
      consultation: acc.consultation + day.consultation,
      tasks: acc.tasks + day.tasks,
      mood: acc.mood + day.mood
    }),
    { consultation: 0, tasks: 0, mood: 0 }
  )
})
</script>
