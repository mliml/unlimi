<template>
  <div class="border-t border-gray-200 bg-white p-4">
    <form @submit.prevent="handleSubmit" class="flex space-x-2">
      <textarea
        v-model="message"
        @keydown.enter.exact.prevent="handleSubmit"
        rows="1"
        :disabled="disabled"
        class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none resize-none disabled:opacity-50 disabled:cursor-not-allowed"
        placeholder="输入您的消息..."
        ref="textareaRef"
      ></textarea>
      <button
        type="submit"
        :disabled="disabled || !message.trim()"
        class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        发送
      </button>
    </form>
    <div class="text-xs text-gray-500 mt-2">
      按 Enter 发送，Shift + Enter 换行
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['send'])

const message = ref('')
const textareaRef = ref(null)

function handleSubmit() {
  if (!message.value.trim() || props.disabled) return

  emit('send', message.value)
  message.value = ''

  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  })
}

watch(message, () => {
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
      textareaRef.value.style.height = textareaRef.value.scrollHeight + 'px'
    }
  })
})
</script>
