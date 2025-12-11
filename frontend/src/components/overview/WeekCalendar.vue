<template>
  <div class="bg-white rounded-2xl p-6 shadow-sm h-full flex flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <h3 class="font-semibold text-textMain flex items-center">
        <svg class="w-5 h-5 mr-2 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        咨询日程
      </h3>
    </div>

    <!-- Week Days -->
    <div class="flex justify-between mb-4">
      <button
        v-for="day in weekDays"
        :key="day.date"
        @click="selectedDay = day.date"
        :class="[
          'flex flex-col items-center p-2 rounded-xl transition-all duration-200',
          selectedDay === day.date
            ? 'bg-accent text-textMain scale-110 shadow-md'
            : 'hover:bg-gray-100 text-textSub'
        ]"
      >
        <span class="text-xs font-medium">{{ day.day }}</span>
        <span :class="[
          'text-lg font-bold mt-1',
          selectedDay === day.date ? 'text-textMain' : 'text-textMain'
        ]">{{ day.date }}</span>
      </button>
    </div>

    <!-- Schedule List - 可滚动内容区域 -->
    <div class="flex-1 overflow-y-auto space-y-3 mb-4">
      <div
        v-for="(activity, index) in todayActivities"
        :key="index"
        class="p-3 rounded-lg hover:bg-gray-50 transition"
      >
        <!-- Activity Info -->
        <div>
          <p class="text-sm font-medium text-textMain mb-1">
            {{ activity.title }}
          </p>
          <div class="flex items-center text-xs text-textSub">
            <svg class="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            {{ activity.time }}
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="todayActivities.length === 0" class="flex flex-col items-center justify-center h-full text-gray-400">
        <svg class="w-12 h-12 mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        <p class="text-sm">今日暂无安排</p>
      </div>
    </div>

    <!-- Book Next Consultation Button - 固定在底部 -->
    <button class="w-full py-3 bg-gradient-to-r from-primary to-primary text-white rounded-xl font-medium hover:shadow-md transition-all duration-200 hover:from-primary hover:to-primary">
      预约下次咨询
    </button>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const selectedDay = ref(22)

// Mock week days
const weekDays = [
  { day: 'Sun', date: 21 },
  { day: 'Mon', date: 22 },
  { day: 'Tue', date: 23 },
  { day: 'Wed', date: 27 },
  { day: 'Thu', date: 28 },
]

// Mock activities
const activities = {
  22: [
    {
      time: '08:00-08:10',
      title: '早晨冥想'
    },
    {
      time: '08:30-09:00',
      title: '感恩日记'
    },
    {
      time: '10:00-10:30',
      title: '正念练习'
    },
    {
      time: '12:30-13:00',
      title: '午间散步'
    },
    {
      time: '14:00-14:30',
      title: '阅读时光'
    },
    {
      time: '16:00-16:45',
      title: '心理咨询'
    },
    {
      time: '17:30-18:00',
      title: '运动锻炼'
    },
    {
      time: '19:00-19:30',
      title: '睡前放松'
    }
  ]
}

const todayActivities = computed(() => {
  return activities[selectedDay.value] || []
})
</script>
