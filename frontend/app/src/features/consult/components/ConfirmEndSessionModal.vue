<template>
  <!-- 遮罩层 -->
  <Transition
    enter-active-class="transition-opacity duration-300 ease-out"
    leave-active-class="transition-opacity duration-200 ease-in"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      v-if="show"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      @click.self="handleClose"
    >
      <!-- 弹窗主体 -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        leave-active-class="transition-all duration-200 ease-in"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          v-if="show"
          class="w-full max-w-md rounded-xl bg-white px-6 py-6 shadow-xl"
          @click.stop
        >
          <!-- 标题 -->
          <h2 class="mb-4 text-center text-xl font-semibold text-gray-800">
            {{ loading ? '正在整理本次咨询记录…' : '确认结束本次咨询?' }}
          </h2>

          <!-- 文本提示（非 loading 状态） -->
          <p v-if="!loading" class="mb-6 text-center text-sm text-gray-600">
            结束后将为你自动整理咨询记录。
          </p>

          <!-- Loading 动画 -->
          <div v-if="loading" class="mb-6 flex justify-center">
            <div class="h-12 w-12 animate-spin rounded-full border-4 border-gray-200 border-t-blue-500"></div>
          </div>

          <!-- 按钮区域（非 loading 状态） -->
          <div v-if="!loading" class="flex gap-3">
            <!-- 暂时离开按钮 -->
            <button
              type="button"
              class="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-3 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
              @click="handleLeave"
            >
              暂时离开
            </button>

            <!-- 结束咨询按钮 -->
            <button
              type="button"
              class="flex-1 rounded-lg bg-red-500 px-4 py-3 text-sm font-medium text-white transition-colors hover:bg-red-600 disabled:cursor-not-allowed disabled:opacity-50"
              @click="handleConfirmEnd"
            >
              结束咨询
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup>
//import { defineProps, defineEmits } from 'vue'

// Props 定义
const props = defineProps({
  show: {
    type: Boolean,
    required: true,
    default: false
  },
  loading: {
    type: Boolean,
    required: true,
    default: false
  },
  onConfirmEnd: {
    type: Function,
    default: null
  },
  onLeave: {
    type: Function,
    default: null
  },
  onClose: {
    type: Function,
    default: null
  }
})

// Emits 定义
const emit = defineEmits(['confirm', 'leave', 'close'])

// 事件处理函数
const handleConfirmEnd = () => {
  if (props.onConfirmEnd) {
    props.onConfirmEnd()
  }
  console.log("Modal emit confirm")
  emit('confirm')
}

const handleLeave = () => {
  if (props.onLeave) {
    props.onLeave()
  }
  emit('leave')
}

const handleClose = () => {
  if (props.loading) return // loading 状态下不允许关闭

  if (props.onClose) {
    props.onClose()
  }
  emit('close')
}
</script>

<style scoped>
/* 自定义 loading 动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
