/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
      colors: {
        background: '#09090b',
        surface: '#18181b',
        surfaceHighlight: '#27272a',
        border: '#27272a',
        textMain: '#f4f4f5',
        textMuted: '#a1a1aa',
        primary: '#06b6d4',
        primaryHover: '#0891b2',
      },
    },
  },
  plugins: [],
}
