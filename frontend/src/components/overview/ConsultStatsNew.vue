<template>
  <div class="bg-white rounded-2xl p-6 shadow-sm">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-semibold text-textMain flex items-center">
        <svg class="w-5 h-5 mr-2 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
        咨询数据新
      </h3>
    </div>

    <!-- Stats Grid - 2x2 -->
    <div class="grid grid-cols-2 gap-4 flex-1">
      <div
        v-for="stat in stats"
        :key="stat.id"
        class="flex flex-col items-center justify-center p-4 rounded-xl bg-gradient-to-br from-gray-50 to-white border border-gray-100 hover:border-secondary transition-all duration-200 group hover:shadow-md"
      >
        <!-- Icon -->
        <div :class="[
          'w-12 h-12 rounded-full flex items-center justify-center mb-3 group-hover:scale-110 transition-transform',
          stat.color === 'purple' ? 'bg-purple-100' :
          stat.color === 'blue' ? 'bg-blue-100' :
          stat.color === 'orange' ? 'bg-orange-100' :
          'bg-green-100'
        ]">
          <svg
            class="w-6 h-6"
            :class="[
              stat.color === 'purple' ? 'text-chartPurple' :
              stat.color === 'blue' ? 'text-chartBlue' :
              stat.color === 'orange' ? 'text-chartOrange' :
              'text-chartGreen'
            ]"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="stat.iconPath" />
          </svg>
        </div>

        <!-- Value -->
        <div class="text-center">
          <p class="text-2xl font-bold text-textMain mb-1">
            {{ stat.value }}
            <span class="text-sm font-normal text-textSub">{{ stat.unit }}</span>
          </p>
          <p class="text-xs text-textSub font-medium">{{ stat.label }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// Mock consult stats data
const stats = [
  {
    id: 1,
    label: '陪伴天数',
    value: 45,
    unit: '天',
    color: 'purple',
    iconPath: 'M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z'
  },
  {
    id: 2,
    label: '咨询时长',
    value: 320,
    unit: '分钟',
    color: 'blue',
    iconPath: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z'
  },
  {
    id: 3,
    label: '咨询次数',
    value: 12,
    unit: '次',
    color: 'orange',
    iconPath: 'M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z'
  },
  {
    id: 4,
    label: '完成任务',
    value: 28,
    unit: '个',
    color: 'green',
    iconPath: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4'
  }
]
</script>
