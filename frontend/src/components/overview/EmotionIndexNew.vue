<template>
  <div class="bg-white rounded-2xl p-6 shadow-sm">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-semibold text-textMain flex items-center">
        <svg class="w-5 h-5 mr-2 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        新情绪指数
      </h3>
      <span class="text-xs text-textSub">本周数据</span>
    </div>

    <!-- Metrics Grid - 横向 1x4 -->
    <div class="grid grid-cols-4 gap-4">
      <div
        v-for="metric in metrics"
        :key="metric.id"
        class="relative p-4 rounded-xl border border-gray-100 hover:border-primary transition-all duration-200 hover:shadow-md group"
      >
        <!-- Empty Data Overlay -->
        <div
          v-if="!hasData"
          class="absolute inset-0 bg-gray-100 bg-opacity-80 rounded-xl flex items-center justify-center z-10"
        >
          <span class="text-sm text-textSub font-medium">数据暂未生成</span>
        </div>

        <!-- Circular Progress -->
        <div class="flex items-center justify-center mb-3">
          <svg class="transform -rotate-90" width="80" height="80">
            <!-- Background circle -->
            <circle
              cx="40"
              cy="40"
              r="32"
              stroke="#e5e7eb"
              stroke-width="6"
              fill="none"
            />
            <!-- Progress circle -->
            <circle
              cx="40"
              cy="40"
              r="32"
              :stroke="getProgressColor(metric.color)"
              stroke-width="6"
              fill="none"
              :stroke-dasharray="circumference"
              :stroke-dashoffset="getProgressOffset(metric.current, metric.target)"
              class="transition-all duration-500"
              stroke-linecap="round"
            />
            <!-- Center text -->
            <text
              x="40"
              y="40"
              text-anchor="middle"
              dy="0.3em"
              class="transform rotate-90"
              style="transform-origin: 40px 40px"
              :fill="getProgressColor(metric.color)"
              font-size="16"
              font-weight="bold"
            >
              {{ metric.current }}
            </text>
          </svg>
        </div>

        <!-- Metric Info -->
        <div class="text-center">
          <p class="text-sm font-semibold text-textMain mb-1">{{ metric.name }}</p>
          <div class="mt-2 flex items-center justify-center">
            <span :class="[
              'text-xs font-medium px-2 py-0.5 rounded-full',
              metric.trend === 'up' ? 'bg-green-100 text-green-700' :
              metric.trend === 'down' ? 'bg-red-100 text-red-700' :
              'bg-gray-100 text-textSub'
            ]">
              <span v-if="metric.trend === 'up'">↑</span>
              <span v-if="metric.trend === 'down'">↓</span>
              {{ metric.changeText }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getLatestEmoScore } from '@/api/emoScore'

const circumference = 2 * Math.PI * 32

// 数据状态
const hasData = ref(false)
const apiData = ref(null)

// 虚构数据（当 API 返回空时使用）
const mockData = {
  stress_score: 45,
  stable_score: 85,
  anxiety_score: 30,
  functional_score: 78,
  stress_score_change: -0.12,
  stable_score_change: 0.08,
  anxiety_score_change: -0.05,
  functional_score_change: 0.06
}

// 格式化变化率为百分比文本
const formatChangeRate = (change) => {
  if (!change) return '0%'
  const percentage = (change * 100).toFixed(0)
  return change > 0 ? `+${percentage}%` : `${percentage}%`
}

// 获取趋势方向
const getTrend = (change) => {
  if (!change) return 'stable'
  return change > 0 ? 'up' : 'down'
}

// 计算 metrics 数据
const metrics = computed(() => {
  const data = hasData.value ? apiData.value : mockData

  return [
    {
      id: 1,
      name: '压力负荷',
      current: data.stress_score || 0,
      target: 100,
      unit: '分',
      color: 'blue',
      trend: getTrend(data.stress_score_change),
      changeText: formatChangeRate(data.stress_score_change)
    },
    {
      id: 2,
      name: '情绪稳定度',
      current: data.stable_score || 0,
      target: 100,
      unit: '分',
      color: 'purple',
      trend: getTrend(data.stable_score_change),
      changeText: formatChangeRate(data.stable_score_change)
    },
    {
      id: 3,
      name: '焦虑指数',
      current: data.anxiety_score || 0,
      target: 100,
      unit: '分',
      color: 'orange',
      trend: getTrend(data.anxiety_score_change),
      changeText: formatChangeRate(data.anxiety_score_change)
    },
    {
      id: 4,
      name: '功能水平',
      current: data.functional_score || 0,
      target: 100,
      unit: '分',
      color: 'green',
      trend: getTrend(data.functional_score_change),
      changeText: formatChangeRate(data.functional_score_change)
    }
  ]
})

// 获取进度颜色
const getProgressColor = (color) => {
  const colors = {
    blue: '#8ECAE6',      // chartBlue
    purple: '#B3B5D8',    // chartPurple
    orange: '#F4A261',    // chartOrange
    green: '#81B29A'      // chartGreen
  }
  return colors[color] || colors.blue
}

// 计算进度偏移
const getProgressOffset = (current, target) => {
  const percentage = (current / target) * 100
  return circumference - (percentage / 100) * circumference
}

// 加载数据
const loadData = async () => {
  try {
    const data = await getLatestEmoScore()
    if (data) {
      hasData.value = true
      apiData.value = data
    } else {
      hasData.value = false
    }
  } catch (error) {
    console.error('Failed to load emo score data:', error)
    hasData.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadData()
})
</script>
