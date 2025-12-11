<template>
  <div class="bg-white rounded-2xl p-6 shadow-sm h-full flex flex-col">
    <!-- Header -->
    <div class="flex items-center justify-between mb-4">
      <h3 class="font-semibold text-textMain flex items-center">
        <svg class="w-5 h-5 mr-2 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        积极习惯清单
      </h3>
    </div>

    <!-- Checklist Items -->
    <div class="space-y-3 flex-1 overflow-y-auto">
      <div
        v-for="item in habitItems"
        :key="item.id"
        @click="toggleItem(item)"
        class="flex items-start space-x-3 p-3 rounded-lg hover:bg-gray-50 transition cursor-pointer group"
      >
          <!-- Checkbox -->
          <div :class="[
            'w-5 h-5 rounded-full border-2 flex items-center justify-center mt-0.5 flex-shrink-0 transition-all',
            item.completed
              ? 'bg-primary border-primary'
              : 'border-gray-300 group-hover:border-primary'
          ]">
            <svg
              v-if="item.completed"
              class="w-3 h-3 text-white"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
            </svg>
          </div>

          <!-- Item Content -->
          <div class="flex-1 min-w-0">
            <p :class="[
              'text-sm font-medium',
              item.completed ? 'text-gray-400 line-through' : 'text-textMain'
            ]">
              {{ item.title }}
            </p>
            <p v-if="item.description" class="text-xs text-textSub mt-1">
              {{ item.description }}
            </p>
            <div v-if="item.dueDate" class="flex items-center mt-1">
              <svg class="w-3 h-3 text-gray-400 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <span class="text-xs text-gray-400">{{ item.dueDate }}</span>
            </div>
          </div>

          <!-- Priority Indicator -->
          <div v-if="item.priority && !item.completed" class="flex-shrink-0">
            <span :class="[
              'inline-block w-2 h-2 rounded-full',
              item.priority === 'high' ? 'bg-red-500' :
              item.priority === 'medium' ? 'bg-tertiary' :
              'bg-blue-400'
            ]"></span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// Mock habit items (only weekly goals)
const habitItems = ref([
  {
    id: 1,
    title: '完成心理评估',
    description: 'PHQ-9 和 GAD-7 量表',
    completed: false,
    priority: 'high',
    dueDate: '周五前'
  },
  {
    id: 2,
    title: '户外活动30分钟',
    description: '至少3次',
    completed: false,
    priority: 'medium',
    dueDate: '本周'
  },
  {
    id: 3,
    title: '社交互动',
    description: '与朋友见面或通话',
    completed: true,
    priority: 'low',
    dueDate: '本周'
  },
  {
    id: 4,
    title: '阅读心理学书籍',
    description: '至少完成一章',
    completed: false,
    priority: 'medium',
    dueDate: '本周'
  },
  {
    id: 5,
    title: '练习放松技巧',
    description: '深呼吸和冥想',
    completed: true,
    priority: 'high',
    dueDate: '本周'
  }
])

// Toggle item completion
const toggleItem = (item) => {
  item.completed = !item.completed
}
</script>
