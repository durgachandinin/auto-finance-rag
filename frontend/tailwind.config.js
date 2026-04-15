/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      colors: {
        brand: {
          50:  '#edeaff',
          100: '#cdc7ff',
          400: '#a99ef7',
          500: '#7c6af7',
          600: '#6a58e6',
          700: '#5646c8',
        },
        surface: {
          900: '#08080f',
          800: '#0c0c1c',
          700: '#12121e',
          600: '#161622',
          500: '#1e1e2e',
          400: '#2a2a3d',
          300: '#3a3a55',
          200: '#4a4a65',
          100: '#7777a0',
        },
      },
      keyframes: {
        fadein: {
          '0%':   { opacity: '0', transform: 'translateY(8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.2' },
        },
        tdot: {
          '0%, 80%, 100%': { opacity: '0.15', transform: 'scale(0.75)' },
          '40%':           { opacity: '1',    transform: 'scale(1)' },
        },
        slideIn: {
          '0%':   { opacity: '0', transform: 'translateX(24px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
      },
      animation: {
        fadein:  'fadein 0.35s ease forwards',
        blink:   'blink 2.5s ease-in-out infinite',
        tdot1:   'tdot 1.4s ease-in-out infinite',
        tdot2:   'tdot 1.4s ease-in-out 0.2s infinite',
        tdot3:   'tdot 1.4s ease-in-out 0.4s infinite',
        slideIn: 'slideIn 0.4s ease forwards',
      },
    },
  },
  plugins: [],
}
