export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // 整体配色
        bg: '#FDFCF8',      /* 整体背景：米白 */
        card: '#FFFFFF',    /* 卡片背景：纯白 */
        textMain: '#2C2A26',/* 主文字：深暖灰 */
        textSub: '#78716C', /* 副文字：暖灰 */

        /* 品牌主色 (保留对象格式以支持 primary-600 等类名) */
        primary: {
          DEFAULT: '#E07A5F', /* 陶土红 - 默认值 */
          50: '#fdf5f3',
          100: '#fbe8e3',
          200: '#f7d0c7',
          300: '#f0ad9e',
          400: '#e68166',
          500: '#E07A5F', /* 主色 */
          600: '#d25e41',
          700: '#b14a32',
          800: '#93402c',
          900: '#7a3829',
        },
        secondary: '#5F7470',/* 矿石蓝绿 */
        tertiary: '#D4A373', /* 暖沙橙 */
        accent: '#F2CC8F',   /* 玉米黄 */

        /* 图表颜色 */
        chartBlue: '#8ECAE6',
        chartPurple: '#B3B5D8',
        chartOrange: '#F4A261',
        chartGreen: '#81B29A',
      },
      fontFamily: {
        serif: ['"Noto Serif SC"', 'serif'],
        sans: ['"Nunito"', 'sans-serif'],
      },
      boxShadow: {
        'soft': '0 10px 40px -10px rgba(44, 42, 38, 0.05)',
        'inner-light': 'inset 0 2px 4px 0 rgba(255, 255, 255, 0.3)',
      },
      borderRadius: {
        'xl': '0.75rem',
        '2xl': '1rem',
      }
    },
  },
  plugins: [],
}
