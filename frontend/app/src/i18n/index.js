import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN'
import enUS from './locales/en-US'

// Get saved language from localStorage, default to Chinese
const savedLocale = localStorage.getItem('unlimi-language') || 'zh-CN'

const i18n = createI18n({
  legacy: false, // Use Composition API mode
  locale: savedLocale,
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS
  }
})

// Helper to change language
export function setLanguage(locale) {
  i18n.global.locale.value = locale
  localStorage.setItem('unlimi-language', locale)
  document.documentElement.lang = locale
}

export default i18n
