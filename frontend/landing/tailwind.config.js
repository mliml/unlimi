export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#FDFCF8',
        card: '#FFFFFF',
        textMain: '#2C2A26',
        textSub: '#78716C',
        primary: {
          DEFAULT: '#E07A5F',
          50: '#fdf5f3',
          100: '#fbe8e3',
          200: '#f7d0c7',
          300: '#f0ad9e',
          400: '#e68166',
          500: '#E07A5F',
          600: '#d25e41',
          700: '#b14a32',
          800: '#93402c',
          900: '#7a3829',
        },
        secondary: '#5F7470',
        tertiary: '#D4A373',
        accent: '#F2CC8F',
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
